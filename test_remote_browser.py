#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
远程浏览器连接测试脚本
用于测试连接 CloakBrowser-Manager 管理的远程浏览器
"""
import requests
from DrissionPage import Chromium, ChromiumOptions
from loguru import logger

# ============================================================
# 配置区域 - 根据你的 CloakBrowser-Manager 部署情况修改
# ============================================================

# CloakBrowser-Manager 地址
CLOAK_MANAGER_URL = "https://cloakbrowser-manager.home.sakuraio.com"

# CloakBrowser-Manager 的 CDP API 端点
# 脚本会自动从 /json/version 获取 WebSocket 地址
CDP_API_URL = "https://cloakbrowser-manager.home.sakuraio.com/api/profiles/0803f920-2345-4e6a-8fe9-471d05036556/cdp"

# ============================================================
# 测试函数
# ============================================================

def test_cloak_api():
    """测试 CloakBrowser-Manager API 是否可达"""
    logger.info("测试 CloakBrowser-Manager API: {}", CLOAK_MANAGER_URL)
    try:
        # 尝试常见的 API 端点
        endpoints = [
            "/api/browsers",
            "/api/browser/list",
            "/browsers",
            "/json/version",
            "/api/v1/browsers",
        ]

        for endpoint in endpoints:
            url = f"{CLOAK_MANAGER_URL}{endpoint}"
            logger.info("尝试: {}", url)
            try:
                resp = requests.get(url, timeout=5, verify=False)
                logger.info("状态码: {}, 响应: {}", resp.status_code, resp.text[:200])
                if resp.status_code == 200:
                    return resp.json() if resp.headers.get('content-type', '').startswith('application/json') else resp.text
            except Exception as e:
                logger.debug("失败: {}", str(e))

    except Exception as e:
        logger.error("API 测试失败: {}", e)
    return None


def test_direct_chrome_debug(port=9222):
    """测试直接连接 Chrome DevTools 端口"""
    logger.info("测试直接连接 Chrome DevTools 端口: {}", port)
    try:
        # 获取浏览器信息
        resp = requests.get(f"http://{CLOAK_MANAGER_URL.split('//')[1].split('/')[0]}:{port}/json/version", timeout=5)
        logger.info("Chrome DevTools 响应: {}", resp.json())
        return resp.json()
    except Exception as e:
        logger.error("连接失败: {}", e)
        return None


def get_ws_url_from_api(api_url):
    """从 CloakBrowser-Manager API 获取实际的 WebSocket 地址
    优先从 /json/version 端点获取，兼容标准 Chrome DevTools Protocol
    """
    logger.info("从 API 获取 WebSocket 地址: {}", api_url)

    # 优先尝试 /json/version 端点 (标准 CDP 方式)
    version_url = f"{api_url}/json/version"
    logger.info("尝试 /json/version 端点: {}", version_url)
    try:
        resp = requests.get(version_url, timeout=10, verify=False)
        if resp.status_code == 200:
            data = resp.json()
            logger.info("/json/version 响应: {}", data)
            ws_url = data.get('webSocketDebuggerUrl')
            if ws_url:
                logger.info("获取到 WebSocket 地址: {}", ws_url)
                return ws_url
    except Exception as e:
        logger.debug("/json/version 请求失败: {}", e)

    # 回退：尝试原始 API 端点
    logger.info("尝试原始 API 端点: {}", api_url)
    try:
        resp = requests.get(api_url, timeout=10, verify=False)
        logger.info("API 响应状态: {}", resp.status_code)
        if resp.status_code == 200:
            data = resp.json()
            logger.info("API 响应: {}", data)
            # 尝试从响应中提取 WebSocket URL
            ws_url = data.get('wsUrl') or data.get('ws_url') or data.get('webSocketDebuggerUrl') or data.get('url')
            if ws_url:
                logger.info("获取到 WebSocket 地址: {}", ws_url)
                return ws_url
    except Exception as e:
        logger.error("获取 WebSocket 地址失败: {}", e)

    logger.warning("无法从 API 响应中提取 WebSocket 地址")
    return None


def test_remote_connection(ws_url=None, http_url=None):
    """测试远程浏览器连接"""
    logger.info("=" * 50)
    logger.info("开始测试远程浏览器连接")

    # 确定连接地址
    address = ws_url or http_url
    if not address:
        logger.error("未指定远程浏览器地址，请设置 CDP_API_URL")
        return False

    # 如果是 API 端点，先获取实际的 WebSocket 地址
    if '/api/' in address and not address.startswith('ws'):
        logger.info("检测到 API 端点，尝试获取 WebSocket 地址...")
        actual_ws_url = get_ws_url_from_api(address)
        if actual_ws_url:
            address = actual_ws_url
        else:
            logger.error("无法从 API 获取 WebSocket 地址，请直接设置 ws:// 格式的地址")
            return False

    logger.info("连接地址: {}", address)

    try:
        # 创建浏览器选项
        options = ChromiumOptions()
        options.set_address(address)

        # 连接浏览器
        logger.info("正在连接远程浏览器...")
        browser = Chromium(addr_or_opts=options)

        # 获取浏览器信息
        logger.info("连接成功!")
        logger.info("浏览器 ID: {}", browser.id)
        logger.info("浏览器地址: {}", browser.address)

        # 获取最新标签页
        tab = browser.latest_tab
        logger.info("当前标签页: {}", tab.title if hasattr(tab, 'title') else 'N/A')

        # 测试访问网页
        logger.info("测试访问百度...")
        tab.get("https://www.baidu.com")
        logger.info("页面标题: {}", tab.title)
        logger.info("HTML 长度: {}", len(tab.html))

        # 测试获取页面元素
        search_input = tab.ele('#kw')
        if search_input:
            logger.info("找到搜索框元素")

        logger.info("测试完成，断开连接")
        # DrissionPage 没有 disconnect() 方法
        # 直接结束脚本即可，浏览器不会被关闭
        # 如需显式断开可调用 browser.reconnect()

        return True

    except Exception as e:
        logger.error("连接失败: {}", e)
        import traceback
        traceback.print_exc()
        return False


def main():
    """主测试流程"""
    logger.info("远程浏览器连接测试工具")
    logger.info("=" * 50)

    # 步骤1: 测试 API 可达性
    logger.info("\n[步骤1] 测试 CloakBrowser-Manager API")
    api_result = test_cloak_api()

    # 步骤2: 尝试连接
    logger.info("\n[步骤2] 测试远程浏览器连接")

    if CDP_API_URL:
        test_remote_connection(http_url=CDP_API_URL)
    elif api_result:
        logger.info("API 返回结果: {}", api_result)
        logger.info("请设置 CDP_API_URL 为 CloakBrowser-Manager 的 CDP 端点")
    else:
        logger.warning("无法自动获取远程浏览器地址")
        logger.info("\n请手动配置:")
        logger.info("1. 访问 {} 查看可用的浏览器", CLOAK_MANAGER_URL)
        logger.info("2. 设置 CDP_API_URL = 'https://<host>/api/profiles/<id>/cdp'")


if __name__ == "__main__":
    # 禁用 SSL 警告
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

    main()
