#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/12
from app.config import c
from app.browser import get_browser
from app.downloader.javdb.downloader import JavDBBrowserDownloader
from app.downloader.default.downloader import FetchRequest
from app.log import setup_loguru
from loguru import logger

setup_loguru()

# 初始化 Chromium
browser = get_browser()
javdb_downloader = JavDBBrowserDownloader(browser)

if __name__ == "__main__":
    html = javdb_downloader.download(
        req=FetchRequest(url="https://javdb.com/v/Ebq2md", timeout=300)
    )
    logger.debug(html)

    html = javdb_downloader.download(
        req=FetchRequest(url="https://javdb.com/anime", timeout=300)
    )
    logger.debug(html)

    for u in [
        "https://javdb.com/v/Ebq2md",
        "https://javdb.com/v/6d45wD",
        "https://javdb.com/v/Mb4mOR",
        "https://javdb.com/v/3na523",
        "https://javdb.com/v/ZNpXDV",
        "https://javdb.com/v/YwZn4p",
        "https://javdb.com/v/Aqknne",
        "https://javdb.com/v/Mb4K9J",
        "https://javdb.com/v/964wNX",
        "https://javdb.com/v/RkJAgD",
        "https://javdb.com/v/mOy3kY",
        "https://javdb.com/v/kK3qMN"
    ]:
        html = javdb_downloader.download(
            req=FetchRequest(url=u, timeout=300)
        )
        logger.debug(html)
