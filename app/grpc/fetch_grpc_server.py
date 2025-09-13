#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/13
import grpc
from app.utils.nettools import get_lan_ip
from concurrent.futures import ThreadPoolExecutor
from app.grpc.fetch_pb2_grpc import add_PageFetchServiceServicer_to_server, PageFetchServiceServicer
from loguru import logger
from app.rod.javdb_browser import browser

from app.config import c

thread_pool = ThreadPoolExecutor(max_workers=10)


def start_grpc_server():
    ip = get_lan_ip()
    logger.info("当前主机IP：{}", ip)

    server = grpc.server(thread_pool=thread_pool)
    add_PageFetchServiceServicer_to_server(
        servicer=PageFetchServiceServicer(),
        server=server
    )
    listen_addr = f"{ip}:{c.grpc_port}"
    server.add_insecure_port(address=listen_addr)
    logger.info(f"Starting server on {listen_addr} ...")
    try:
        browser.start()
        server.start()
        server.wait_for_termination()
    except Exception as e:
        logger.warning(str(e))
    finally:
        browser.stop()
