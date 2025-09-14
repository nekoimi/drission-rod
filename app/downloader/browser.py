#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/14
import abc

from DrissionPage import Chromium
from DrissionPage.items import MixTab
from pydantic import BaseModel


class FetchRequest(BaseModel):
    url: str
    timeout: int | None = 60


class BrowserDownloader(abc.ABC):
    browser: Chromium

    def __init__(self, browser: Chromium):
        self.browser = browser

    def wait_page_complete(self, page_tab: MixTab):
        page_tab.wait.doc_loaded()
        while page_tab.states.ready_state in "connectingloadinginteractive":
            page_tab.wait(1, 3.5)

    @abc.abstractmethod
    def download(self, req: FetchRequest) -> str:
        pass
