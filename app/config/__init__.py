#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/12
from app.config.config import Config
from loguru import logger

c = Config()
logger.info("配置信息：{}", c.model_dump_json())

__all__ = ["c"]
