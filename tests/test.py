#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/12
import os

from DrissionPage import Chromium, ChromiumOptions
from DrissionPage.common import Settings

Settings.set_language("zh_cn")  # 设置为中文时，填入'zh_cn'

if __name__ == "__main__":
    co = ChromiumOptions()
    # co.set_user_data_path(path='C:\\Users\\yangj\\Downloads\\results\\temp')
    browser = Chromium(co)
    tab = browser.new_tab(url="https://mvnrepository.com/")
    tab.wait.title_change(text="Maven", exclude=False, timeout=60)
    # browser.quit()
