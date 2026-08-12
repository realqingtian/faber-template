#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : application.py
@Create Time    : 2026-08-12 星期三 18:58:21
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 
"""
from fastapi import FastAPI

from app.core.config import get_settings

settings = get_settings()


def create_app():
    """
    创建并返回一个FastAPI应用实例
    """
    app = FastAPI(
        title=settings.APP_NAME,
        description=settings.APP_DESCRIPTION,
        version=settings.APP_VERSION,
        debug=settings.APP_DEBUG,
        docs_url=settings.APP_API_DOCS_URL,
        redoc_url=settings.APP_REDOC_URL,
        openapi_url=settings.APP_OPENAPI_URL,
    )

    return app
