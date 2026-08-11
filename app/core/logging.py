#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : logging.py
@Create Time    : 2026-08-11 星期二 22:00:46
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 配置并清理应用的 Loguru 控制台与文件日志处理器
"""
import sys

from loguru import logger

from app.core.config import Settings


PLAIN_LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)


def configure_logging(settings: Settings) -> tuple[int, ...]:
    """根据应用配置创建控制台与文件日志处理器。"""
    settings.LOG_FILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    logger.remove()
    handler_ids: list[int] = []
    try:
        handler_ids.append(
            logger.add(
                sys.stderr,
                level=settings.LOG_LEVEL,
                format=PLAIN_LOG_FORMAT,
                colorize=False if settings.LOG_SERIALIZE else None,
                serialize=settings.LOG_SERIALIZE,
                diagnose=False,
            )
        )
        handler_ids.append(
            logger.add(
                settings.LOG_FILE_PATH,
                level=settings.LOG_LEVEL,
                format=PLAIN_LOG_FORMAT,
                colorize=False,
                serialize=settings.LOG_SERIALIZE,
                diagnose=False,
                encoding="utf-8",
            )
        )
    except BaseException:
        shutdown_logging(tuple(handler_ids))
        raise
    return tuple(handler_ids)


def shutdown_logging(handler_ids: tuple[int, ...]) -> None:
    """移除并关闭本次应用生命周期创建的日志处理器。"""
    for handler_id in handler_ids:
        logger.remove(handler_id)


__all__ = ["configure_logging", "logger", "shutdown_logging"]
