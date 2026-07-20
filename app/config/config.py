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
    # CloakBrowser-Manager 远程浏览器配置
    cloak_manager_url: str = ""
    cloak_profile_id: str = ""
    cloak_auth_token: str = ""
    cloak_idle_timeout: int = 300  # 空闲超时秒数，默认5分钟
    # javdb
    javdb_username: str = ""
    javdb_password: str = ""
