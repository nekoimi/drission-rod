#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# nekoimi 2025/9/12
import uvicorn
from fastapi import FastAPI
from fastapi.requests import Request
from fastapi.responses import JSONResponse
from loguru import logger

from app.config import c
from app.utils.nettools import get_lan_ip
from app.rod.javdb_browser import browser, FetchRequest

app = FastAPI()


@app.on_event("startup")
async def startup_event():
    browser.start()


@app.on_event("shutdown")
async def shutdown_event():
    browser.stop()


@app.post("/fetch")
async def fetch(req: FetchRequest):
    html = await browser.download(req=req)
    return JSONResponse(
        status_code=200,
        content={
            "code": 0,
            "html": html
        }
    )


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "error": str(exc),
            "url": str(request.url)
        },
    )


if __name__ == "__main__":
    logger.info("服务启动中...")

    ip = get_lan_ip()
    logger.info("当前主机IP：{}", ip)

    uvicorn.run(
        app=app,
        host=ip,
        port=c.port,
        log_config=None,
        log_level=None,
    )
