#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/12
import logging
from loguru import logger
from app.config import c


class InterceptHandler(logging.Handler):
    def emit(self, record):
        # Get corresponding Loguru level
        try:
            level = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        # Find caller to get correct stack depth
        frame, depth = logging.currentframe(), 2
        while frame.f_back and frame.f_code.co_filename == logging.__file__:
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level, record.getMessage()
        )


# 配置日志记录器
def setup_loguru():
    # Remove existing handlers
    for handler in logging.root.handlers[:]:
        logging.root.removeHandler(handler)

    # Intercept standard logging
    if c.debug:
        logging.basicConfig(handlers=[InterceptHandler()], level=logging.DEBUG)
    else:
        logging.basicConfig(handlers=[InterceptHandler()], level=logging.INFO)

    # 添加文件输出处理器
    for level in ["DEBUG", "INFO", "WARNING", "ERROR"]:
        logger.add(
            "logs/" + level.lower() + ".log",
            level=level,
            rotation="100 MB",
            retention="7 days",
            format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} - {message}",
            enqueue=True,
        )

    loggers = (
        "uvicorn",
        "uvicorn.access",
        "uvicorn.error",
        "fastapi",
        "asyncio",
        "starlette",
    )

    for logger_name in loggers:
        logging_logger = logging.getLogger(logger_name)
        logging_logger.handlers = []
        logging_logger.propagate = True

    logger.debug("setup loguru logging...")
