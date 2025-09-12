#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/12
import socket


def get_lan_ip():
    """
    获取当前主机IP
    :return:
    """
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except OSError:
        return "127.0.0.1"
