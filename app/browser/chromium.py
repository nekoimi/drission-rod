#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/14
import threading
import time

import requests
from DrissionPage import Chromium, ChromiumOptions
from DrissionPage.common import Settings
from loguru import logger

from app.config import c

_browser: Chromium | None = None
_browser_lock: threading.Lock = threading.Lock()
_last_active_time: float = 0
_idle_checker_running: bool = False
_idle_checker_thread: threading.Thread | None = None

Settings.set_language("zh_cn")


def _get_headers() -> dict:
    """获取 API 请求头"""
    headers = {"Content-Type": "application/json"}
    if c.cloak_auth_token:
        headers["Authorization"] = f"Bearer {c.cloak_auth_token}"
    return headers


def _start_remote_browser() -> bool:
    """通过 CloakBrowser-Manager API 启动远程浏览器

    Returns:
        是否启动成功
    """
    if not c.cloak_manager_url or not c.cloak_profile_id:
        logger.error("未配置 CloakBrowser-Manager")
        return False

    api_url = f"{c.cloak_manager_url}/api/profiles/{c.cloak_profile_id}/launch"
    try:
        logger.info("启动远程浏览器: {}", api_url)
        resp = requests.post(api_url, headers=_get_headers(), timeout=30, verify=False)
        if resp.status_code == 200:
            data = resp.json()
            logger.info("远程浏览器启动成功: {}", data)
            return True
        elif resp.status_code == 409:
            # 浏览器已在运行
            logger.info("远程浏览器已在运行")
            return True
        else:
            logger.error("启动远程浏览器失败, 状态码: {}, 响应: {}", resp.status_code, resp.text)
            return False
    except Exception as e:
        logger.error("启动远程浏览器异常: {}", e)
        return False


def _stop_remote_browser() -> bool:
    """通过 CloakBrowser-Manager API 停止远程浏览器

    Returns:
        是否停止成功
    """
    if not c.cloak_manager_url or not c.cloak_profile_id:
        return False

    api_url = f"{c.cloak_manager_url}/api/profiles/{c.cloak_profile_id}/stop"
    try:
        logger.info("停止远程浏览器: {}", api_url)
        resp = requests.post(api_url, headers=_get_headers(), timeout=10, verify=False)
        if resp.status_code == 200:
            logger.info("远程浏览器已停止")
            return True
        elif resp.status_code == 404:
            # 浏览器未运行
            logger.info("远程浏览器未在运行")
            return True
        else:
            logger.error("停止远程浏览器失败, 状态码: {}, 响应: {}", resp.status_code, resp.text)
            return False
    except Exception as e:
        logger.error("停止远程浏览器异常: {}", e)
        return False


def _get_ws_url() -> str | None:
    """从 CloakBrowser-Manager 获取远程浏览器的 WebSocket 地址

    Returns:
        WebSocket 地址 (wss://...) 或 None
    """
    if not c.cloak_manager_url or not c.cloak_profile_id:
        return None

    api_url = f"{c.cloak_manager_url}/api/profiles/{c.cloak_profile_id}/cdp/json/version"
    try:
        resp = requests.get(api_url, headers=_get_headers(), timeout=10, verify=False)
        if resp.status_code == 200:
            data = resp.json()
            ws_url = data.get("webSocketDebuggerUrl")
            if ws_url:
                logger.info("获取到远程 WebSocket 地址: {}", ws_url)
                return ws_url
            logger.warning("API 响应中未找到 webSocketDebuggerUrl: {}", data)
        else:
            logger.error("获取 WebSocket 地址失败, 状态码: {}", resp.status_code)
    except Exception as e:
        logger.error("获取 WebSocket 地址异常: {}", e)

    return None


def _connect_remote_browser() -> Chromium | None:
    """连接远程浏览器

    Returns:
        Chromium 对象或 None
    """
    ws_url = _get_ws_url()
    if not ws_url:
        return None

    try:
        options = ChromiumOptions()
        options.set_address(ws_url)
        browser = Chromium(addr_or_opts=options)
        logger.info("成功连接远程浏览器, ID: {}", browser.id)
        return browser
    except Exception as e:
        logger.error("连接远程浏览器失败: {}", e)
        return None


def _update_activity():
    """更新最后活跃时间"""
    global _last_active_time
    _last_active_time = time.time()


def _check_idle():
    """空闲检测线程函数"""
    global _browser, _idle_checker_running

    logger.info("空闲检测器已启动, 超时时间: {}秒", c.cloak_idle_timeout)

    while _idle_checker_running:
        try:
            time.sleep(60)  # 每60秒检查一次

            if not _idle_checker_running:
                break

            with _browser_lock:
                if _browser is None:
                    continue

                idle_time = time.time() - _last_active_time
                if idle_time > c.cloak_idle_timeout:
                    logger.info("浏览器空闲 {}秒, 超过阈值 {}秒, 准备停止", int(idle_time), c.cloak_idle_timeout)
                    try:
                        _browser.quit(del_data=False)
                    except Exception as e:
                        logger.warning("关闭浏览器连接时出错: {}", e)
                    _browser = None
                    _stop_remote_browser()
                    logger.info("远程浏览器已停止")
                else:
                    remaining = c.cloak_idle_timeout - idle_time
                    logger.debug("浏览器空闲 {}秒, 剩余 {}秒后停止", int(idle_time), int(remaining))

        except Exception as e:
            logger.error("空闲检测器异常: {}", e)

    logger.info("空闲检测器已停止")


def start_idle_checker():
    """启动空闲检测器"""
    global _idle_checker_running, _idle_checker_thread

    if _idle_checker_thread and _idle_checker_thread.is_alive():
        logger.warning("空闲检测器已在运行")
        return

    _idle_checker_running = True
    _idle_checker_thread = threading.Thread(target=_check_idle, daemon=True, name="idle-checker")
    _idle_checker_thread.start()
    logger.info("空闲检测器线程已启动")


def stop_idle_checker():
    """停止空闲检测器"""
    global _idle_checker_running

    _idle_checker_running = False
    logger.info("空闲检测器正在停止...")


def get_browser() -> Chromium:
    """获取浏览器实例，不存在则启动远程浏览器

    Returns:
        Chromium 浏览器对象
    """
    global _browser

    with _browser_lock:
        if _browser is None or not _browser.states.is_alive:
            # 关闭旧连接
            if _browser is not None:
                try:
                    _browser.quit(del_data=False)
                except Exception:
                    pass
                _browser = None

            # 启动远程浏览器
            logger.info("远程浏览器未运行，正在启动...")
            if not _start_remote_browser():
                raise RuntimeError("无法启动远程浏览器，请检查 CloakBrowser-Manager 配置")

            # 等待浏览器就绪
            time.sleep(2)

            # 连接远程浏览器
            _browser = _connect_remote_browser()
            if _browser is None:
                raise RuntimeError("无法连接远程浏览器")

        _update_activity()
        return _browser


def close_browser():
    """关闭浏览器连接（不停止远程浏览器）"""
    global _browser

    with _browser_lock:
        if _browser is not None:
            logger.debug("关闭浏览器连接...")
            try:
                _browser.quit(del_data=False)
            except Exception as e:
                logger.warning("关闭浏览器连接时出错: {}", e)
            _browser = None


def shutdown_browser():
    """完全关闭：停止远程浏览器 + 停止空闲检测器"""
    global _browser

    stop_idle_checker()

    with _browser_lock:
        if _browser is not None:
            logger.debug("关闭浏览器连接...")
            try:
                _browser.quit(del_data=False)
            except Exception as e:
                logger.warning("关闭浏览器连接时出错: {}", e)
            _browser = None

    _stop_remote_browser()
    logger.info("远程浏览器已完全关闭")
