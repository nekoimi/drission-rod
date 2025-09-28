#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/14
from loguru import logger

from app.downloader.browser import BrowserDownloader, FetchRequest


class DefaultBrowserDownloader(BrowserDownloader):

    def download(self, req: FetchRequest) -> str:
        logger.debug(f"开始下载页面：{req.url} ...")
        cur_tab = None
        try:
            cur_tab = self.browser.new_tab()
            cur_tab.get(url=req.url, show_errmsg=True, interval=5, timeout=req.timeout)
            self.wait_page_complete(cur_tab)
            return cur_tab.html
        finally:
            if cur_tab:
                cur_tab.close()
                logger.debug(f"关闭页面：{req.url}")
