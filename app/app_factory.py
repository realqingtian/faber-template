#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : app_factory.py
@Create Time    : 2026-08-11 星期二 17:08:16
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 创建并装配 FastAPI 应用实例
"""
from fastapi import FastAPI

from app.api.router import api_router
from app.core.config import get_settings
from app.core.lifespan import application_lifespan
from app.core.logger import setup_logging


def create_app() -> FastAPI:
    """创建并返回配置完整的 FastAPI 应用实例。"""
    settings = get_settings()
    setup_logging(settings)

    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        debug=settings.APP_DEBUG,
        docs_url=settings.APP_API_DOCS,
        redoc_url=settings.APP_API_REDOC,
        openapi_url=settings.APP_API_OPENAPI,
        lifespan=application_lifespan,
    )
    app.include_router(api_router)
    return app
