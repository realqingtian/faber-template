#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : lifespan.py
@Create Time    : 2026-08-11 星期二 21:11:36
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 管理 FastAPI 应用启动与退出期间的长生命周期资源
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.database.mongodb import mongodb


@asynccontextmanager
async def application_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """在应用启动和退出时管理 MongoDB 连接。"""
    await mongodb.connect()
    app.state.mongodb = mongodb
    try:
        yield
    finally:
        await mongodb.disconnect()


__all__ = ["application_lifespan"]
