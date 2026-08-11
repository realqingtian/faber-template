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

from app.core.config import get_settings
from app.core.logging import configure_logging, logger, shutdown_logging
from app.database.mongodb import mongodb


@asynccontextmanager
async def application_lifespan(app: FastAPI) -> AsyncIterator[None]:
    """在应用启动和退出时管理日志与 MongoDB 资源。"""
    settings = get_settings()
    logging_handler_ids = configure_logging(settings)
    try:
        logger.info(
            "Application logging initialized: level={}, serialize={}, file={}",
            settings.LOG_LEVEL,
            settings.LOG_SERIALIZE,
            settings.LOG_FILE_PATH,
        )
        await mongodb.connect()
        app.state.mongodb = mongodb
        try:
            yield
        finally:
            await mongodb.disconnect()
    finally:
        shutdown_logging(logging_handler_ids)


__all__ = ["application_lifespan"]
