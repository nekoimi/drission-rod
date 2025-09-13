#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/12
from loguru import logger
from app.grpc import start_grpc_server

if __name__ == "__main__":
    logger.info("服务启动中...")
    start_grpc_server()
