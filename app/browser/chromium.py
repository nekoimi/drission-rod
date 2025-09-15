#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/14
import os
from DrissionPage import Chromium, ChromiumOptions
from DrissionPage.common import Settings
from loguru import logger

from app.config import c

_browser: Chromium | None = None

Settings.set_language("zh_cn")  # 设置为中文时，填入'zh_cn'


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
        # 判断 DISPLAY 环境变量
        display_env = os.environ.get("DISPLAY", "")
        if display_env == ":99":
            # 在 Xvfb 虚拟桌面下 → 默认启用有界面模式
            logger.info("检测到 DISPLAY=:99，启动有界面模式（非 headless）")
            options.headless(on_off=False)
        else:
            if c.chromium_headless:
                options.headless(on_off=True)
                options.set_argument("--headless=new")
            else:
                options.headless(on_off=False)
        if c.chromium_proxy:
            options.set_proxy(proxy=c.chromium_proxy)
        options.set_user_agent(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        )
        options.set_user_data_path(path=c.chromium_data_dir)
        _browser = Chromium(addr_or_opts=options)
        logger.debug("初始化chromium...")
    return _browser
