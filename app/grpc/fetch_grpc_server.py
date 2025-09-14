#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/13
from concurrent.futures import ThreadPoolExecutor

from DrissionPage import Chromium

from app.downloader.browser import BrowserDownloader
from app.downloader.default.downloader import DefaultBrowserDownloader, FetchRequest
from app.downloader.javdb.downloader import JavDBBrowserDownloader
from app.downloader.sehuatang.downloader import SehuatangBrowserDownloader
from app.grpc.fetch_pb2_grpc import PageFetchServiceServicer
from app.grpc.fetch_pb2 import FetchResponse

thread_pool = ThreadPoolExecutor(max_workers=10)


class ChromiumPageFetchServiceServicer(PageFetchServiceServicer):
    browser: Chromium
    default_downloader: BrowserDownloader
    javdb_downloader: BrowserDownloader
    sehuatang_downloader: BrowserDownloader

    def __init__(self, browser: Chromium):
        self.browser = browser
        self.default_downloader = DefaultBrowserDownloader(self.browser)
        self.javdb_downloader = JavDBBrowserDownloader(self.browser)
        self.sehuatang_downloader = SehuatangBrowserDownloader(self.browser)

    def Fetch(self, request, context):
        try:
            html = self.default_downloader.download(
                req=FetchRequest(url=request.url, timeout=request.timeout)
            )
            return FetchResponse(success=True, html=html)
        except Exception as e:
            return FetchResponse(success=False, error=str(e))

    def FetchJavDB(self, request, context):
        try:
            html = self.javdb_downloader.download(
                req=FetchRequest(url=request.url, timeout=request.timeout)
            )
            return FetchResponse(success=True, html=html)
        except Exception as e:
            return FetchResponse(success=False, error=str(e))

    def FetchSehuatang(self, request, context):
        try:
            html = self.sehuatang_downloader.download(
                req=FetchRequest(url=request.url, timeout=request.timeout)
            )
            return FetchResponse(success=True, html=html)
        except Exception as e:
            return FetchResponse(success=False, error=str(e))
