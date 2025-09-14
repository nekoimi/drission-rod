#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/12
from pydantic_settings import BaseSettings, SettingsConfigDict


class Config(BaseSettings):
    """
    全局项目配置

    使用：
        from app.config import c
    """

    model_config = SettingsConfigDict(
        env_file=".env", case_sensitive=False, validate_default=True
    )

    debug: bool = True
    grpc_port: int = 8191
    # 浏览器配置
    chromium_headless: bool = False
    chromium_proxy: str = "http://127.0.0.1:12080"
    chromium_data_dir: str
    # javdb
    javdb_username: str = ""
    javdb_password: str = ""
