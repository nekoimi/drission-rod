#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/14
from app.config import c
from loguru import logger
from DrissionPage import Chromium, ChromiumOptions

_browser: Chromium | None = None


def setup_browser() -> Chromium:
    global _browser
    if _browser is None:
        # 初始化浏览器
        options = ChromiumOptions()
        options.no_imgs(False)  # 设置不加载图片
        options.mute(True)  # 静音
        options.set_argument("--disable-software-rasterizer")
        options.set_argument("--disable-gpu")
        options.set_argument("--no-sandbox")
        options.set_argument("--disable-dev-shm-usage")
        options.set_argument("--disable-extensions")
        options.set_argument("--window-size", "1920,1080")
        if c.chromium_headless:
            options.headless(on_off=True)
            options.set_argument("--headless=new")
        if c.chromium_proxy:
            options.set_proxy(proxy=c.chromium_proxy)
        options.set_user_agent(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        )
        options.set_user_data_path(path=c.chromium_data_dir)
        _browser = Chromium(addr_or_opts=options)
        logger.debug("初始化chromium...")
    return _browser
