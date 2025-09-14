#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/12
from concurrent.futures import ThreadPoolExecutor

import grpc
from loguru import logger

from app.config import c
from app.grpc.fetch_grpc_server import ChromiumPageFetchServiceServicer
from app.grpc.fetch_pb2_grpc import add_PageFetchServiceServicer_to_server
from app.browser import setup_browser
from app.utils.nettools import get_lan_ip
from app.log import setup_loguru

setup_loguru()
thread_pool = ThreadPoolExecutor(max_workers=10)
# 初始化 Chromium
browser = setup_browser()


def serve():
    logger.info("服务启动中...")

    ip = get_lan_ip()
    logger.info("当前主机IP：{}", ip)

    try:
        # 启动 grpc 服务
        server = grpc.server(thread_pool=thread_pool)
        add_PageFetchServiceServicer_to_server(
            servicer=ChromiumPageFetchServiceServicer(browser=browser), server=server
        )
        listen_addr = f"0.0.0.0:{c.grpc_port}"
        server.add_insecure_port(address=listen_addr)
        logger.info(f"Starting server on {listen_addr} ...")
        server.start()
        server.wait_for_termination()
    except Exception as e:
        logger.warning(str(e))
    finally:
        logger.debug("quit chromium...")
        browser.quit(del_data=c.debug)


if __name__ == "__main__":
    serve()
