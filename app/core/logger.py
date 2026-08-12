#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : logger.py
@Create Time    : 2026-08-12 星期三 18:56:53
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 
"""
from __future__ import annotations

import sys

from loguru import logger

from app.core.config import get_settings


__all__ = ["logger"]

_LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


settings = get_settings()
diagnose = settings.APP_DEBUG and settings.RUN_MODE != "production"

logger.remove()
logger.add(
    sys.stderr,
    format=_LOG_FORMAT,
    level=settings.LOG_LEVEL,
    serialize=settings.LOG_SERIALIZE,
    backtrace=settings.APP_DEBUG,
    diagnose=diagnose,
)

if settings.LOG_OUTPUT_FILE:
    logger.add(
        settings.LOG_DIR / settings.ACCESS_LOG_FILE,
        format=_LOG_FORMAT,
        level=settings.LOG_LEVEL,
        serialize=settings.LOG_SERIALIZE,
        backtrace=settings.APP_DEBUG,
        diagnose=diagnose,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
        encoding="utf-8",
        enqueue=True,
    )
    logger.add(
        settings.LOG_DIR / settings.ERROR_LOG_FILE,
        format=_LOG_FORMAT,
        level="ERROR",
        serialize=settings.LOG_SERIALIZE,
        backtrace=settings.APP_DEBUG,
        diagnose=diagnose,
        rotation=settings.LOG_ROTATION,
        retention=settings.LOG_RETENTION,
        compression="zip",
        encoding="utf-8",
        enqueue=True,
    )


if __name__ == "__main__":
    logger.info("Test INFO logger")
