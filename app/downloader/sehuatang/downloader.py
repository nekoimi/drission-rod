#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/14
from DrissionPage.items import MixTab
from loguru import logger

from app.downloader.browser import BrowserDownloader, FetchRequest


class SehuatangBrowserDownloader(BrowserDownloader):

    def r18modal_check(self, page_tab: MixTab):
        content = page_tab.ele("#hd")
        if not content:
            logger.debug("not find content")
            r18btn = page_tab.ele("css:body>a:nth-child(5)")
            if r18btn:
                logger.debug(f"点击访问按钮: {r18btn.text}")
                r18btn.click.left()
                self.wait_page_complete(page_tab)

    def download(self, req: FetchRequest) -> str:
        logger.debug(f"开始下载页面：{req.url} ...")
        cur_tab = None
        try:
            cur_tab = self.browser.new_tab()
            cur_tab.get(url=req.url, show_errmsg=True, interval=5, timeout=req.timeout)
            self.wait_page_complete(cur_tab)
            # 检查r18确认弹窗
            self.r18modal_check(cur_tab)
            return cur_tab.html
        finally:
            if cur_tab:
                cur_tab.close()
                logger.debug(f"关闭页面：{req.url}")
