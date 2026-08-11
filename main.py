#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : main.py
@Create Time    : 2026-08-11 星期二 17:00:17
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    :
"""
from app.core.config import get_settings
from app.app_factory import create_app


settings = get_settings()

app = create_app()


if __name__ == '__main__':
    import uvicorn

    uvicorn.run(
        app='main:app',
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
    )