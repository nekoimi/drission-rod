#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/12
from DrissionPage import Chromium, ChromiumOptions
from DrissionPage.items import MixTab

from app.config import c
from loguru import logger
from pydantic import BaseModel


class FetchRequest(BaseModel):
    url: str
    timeout: int | None = 60
    username: str = ""
    password: str = ""


def wait_page_complete(page_tab: MixTab):
    page_tab.wait.doc_loaded()
    while page_tab.states.ready_state in 'connecting' 'loading' 'interactive':
        page_tab.wait(1, 3.5)


class JavDBBrowser(object):
    browser: Chromium

    def start(self):
        options = ChromiumOptions()
        options.no_imgs(True)  # 设置不加载图片
        options.mute(True)  # 静音
        options.headless(on_off=c.headless)  # 无头模式
        options.set_argument("--window-size", "1920,1080")
        options.set_user_data_path(path=c.user_data_dir)
        if c.proxy:
            options.set_proxy(proxy=c.proxy)
        options.set_user_agent(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Safari/537.36"
        )
        self.browser = Chromium(addr_or_opts=options)

    def stop(self):
        self.browser.quit(del_data=c.debug)

    def download(self, req: FetchRequest) -> str:
        logger.debug(f"开始下载页面：{req.url} ...")
        cur_tab = None
        try:
            cur_tab = self.browser.new_tab()
            cur_tab.get(
                url=req.url,
                show_errmsg=True,
                interval=5,
                timeout=req.timeout
            )
            wait_page_complete(page_tab=cur_tab)
            # 检查r18确认弹窗
            r18modal = cur_tab.ele("css:div.modal.is-active.over18-modal")
            if r18modal:
                logger.debug("find r18modal")
                r18btn = r18modal.ele("css:a.button.is-success.is-large")
                if r18btn:
                    logger.debug(f"点击访问按钮: {r18btn.text}")
                    r18btn.click.left()
                    wait_page_complete(page_tab=cur_tab)
            # 检查是否需要登录

            return cur_tab.html
        finally:
            if cur_tab:
                # cur_tab.close()
                logger.debug(f"关闭页面：{req.url}")
