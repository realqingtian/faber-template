#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : app_factory.py
@Create Time    : 2026-08-11 星期二 17:08:16
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 创建并配置 FastAPI 应用实例及其生命周期
"""
from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.database import MongoDatabase, mongodb


def create_app(database: MongoDatabase | None = None) -> FastAPI:
    """创建并返回配置完整的 FastAPI 应用实例。"""
    settings = get_settings()
    database_manager = database if database is not None else mongodb

    @asynccontextmanager
    async def lifespan(app: FastAPI) -> AsyncIterator[None]:
        """在应用启动和退出时管理 MongoDB 连接。"""
        await database_manager.connect()
        app.state.mongodb = database_manager
        try:
            yield
        finally:
            await database_manager.disconnect()

    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        debug=settings.APP_DEBUG,
        docs_url=settings.APP_API_DOCS,
        redoc_url=settings.APP_API_REDOC,
        openapi_url=settings.APP_API_OPENAPI,
        lifespan=lifespan,
    )
    app.include_router(api_router)
    return app
