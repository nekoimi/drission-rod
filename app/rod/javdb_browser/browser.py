#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/12
from ddddocr import DdddOcr
from DrissionPage import Chromium, ChromiumOptions
from DrissionPage.items import MixTab

from app.config import c
from loguru import logger
from pydantic import BaseModel


class FetchRequest(BaseModel):
    url: str
    timeout: int | None = 60


def wait_page_complete(page_tab: MixTab):
    page_tab.wait.doc_loaded()
    while page_tab.states.ready_state in 'connecting' 'loading' 'interactive':
        page_tab.wait(1, 3.5)


class JavDBBrowser(object):
    browser: Chromium
    ocr: DdddOcr

    def start(self):
        # 初始化浏览器
        options = ChromiumOptions()
        options.no_imgs(False)  # 设置不加载图片
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
        # 初始化ocr
        self.ocr = DdddOcr(show_ad=False)
        logger.info("javdb browser start")

    def stop(self):
        self.browser.quit(del_data=c.debug)
        logger.info("javdb browser stop")

    def login(self, page_tab: MixTab):
        raw_url = page_tab.url
        login_num = 1
        while login_num <= 5:
            wait_page_complete(page_tab)
            el_login_pwd = page_tab.ele("#password")
            el_login_rember = page_tab.ele("#remember")
            if not el_login_pwd or not el_login_rember:
                break

            logger.debug("need login")
            # 验证码
            captcha_img = page_tab.ele("css:img.rucaptcha-image")
            if not captcha_img:
                break

            logger.debug("captcha image")
            # 账号
            el_username = page_tab.ele("#email")
            # 验证码
            el_captcha_image = page_tab.ele("css:input.rucaptcha-input")
            # 提交按钮
            el_submit_btn = page_tab.ele('css:input[type="submit"].button.is-link')
            if not el_username or not el_captcha_image or not el_submit_btn:
                break

            logger.debug("input login")
            # 处理验证码
            img_bytes = captcha_img.get_screenshot(as_bytes="png")
            img_code_value = self.ocr.classification(img=img_bytes, png_fix=True)
            logger.debug(f"OCR识别结果：{img_code_value}")
            page_tab.wait(0.5, 3.5)
            el_username.input(c.javdb_username)
            page_tab.wait(0.5, 3.5)
            el_login_pwd.input(c.javdb_password)
            page_tab.wait(0.5, 3.5)
            el_captcha_image.input(img_code_value)
            page_tab.wait(0.5, 3.5)
            el_login_rember.click.left()
            page_tab.wait(0.5, 3.5)
            # login click
            el_submit_btn.click.left()
            logger.debug(f"javdb login [{login_num}] {raw_url} ...")
            wait_page_complete(page_tab)
            page_tab.refresh()
            login_num += 1

    async def download(self, req: FetchRequest) -> str:
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
            wait_page_complete(cur_tab)
            # 检查r18确认弹窗
            r18modal = cur_tab.ele("css:div.modal.is-active.over18-modal")
            if r18modal:
                logger.debug("find r18modal")
                r18btn = r18modal.ele("css:a.button.is-success.is-large")
                if r18btn:
                    logger.debug(f"点击访问按钮: {r18btn.text}")
                    r18btn.click.left()
                    wait_page_complete(cur_tab)
            # 检查是否需要登录
            self.login(cur_tab)
            return cur_tab.html
        finally:
            if cur_tab:
                cur_tab.close()
                logger.debug(f"关闭页面：{req.url}")
