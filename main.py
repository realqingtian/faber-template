#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : main.py
@Create Time    : 2026-08-12 星期三 18:17:47
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 
"""
import uvicorn

from app.application import create_app
from app.core.config import get_settings

settings = get_settings()
app = create_app()

if __name__ == '__main__':
    uvicorn.run(
        app='main:app',
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG
    )
