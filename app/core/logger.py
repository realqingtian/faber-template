#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : logger.py
@Create Time    : 2026-08-11 星期二 22:34:34
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 统一配置 Loguru 并接管应用标准日志
"""
from __future__ import annotations

import inspect
import logging
import sys
from pathlib import Path
from typing import TYPE_CHECKING

from loguru import logger

from app.core.config import PROJECT_ROOT, Settings


if TYPE_CHECKING:
    from loguru import Record


_PLAIN_LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - "
    "<level>{message}</level>"
)
_STANDARD_LOGGER_NAMES = (
    "uvicorn",
    "uvicorn.error",
    "uvicorn.access",
    "fastapi",
)


def _is_normal_record(record: Record) -> bool:
    """仅允许低于 ERROR 的普通日志进入普通文件。"""
    return record["level"].no < logging.ERROR


def _resolve_error_level(configured_level: str) -> str:
    """确保错误文件最低从 ERROR 级别开始记录。"""
    if logger.level(configured_level).no >= logging.ERROR:
        return configured_level
    return "ERROR"


def _resolve_log_path(path: Path) -> Path:
    """将日志文件路径解析为项目根目录下的绝对路径。"""
    if path.is_absolute():
        return path.resolve()
    return (PROJECT_ROOT / path).resolve()


class _InterceptHandler(logging.Handler):
    """将标准库日志记录转发到 Loguru。"""

    def emit(self, record: logging.LogRecord) -> None:
        """保留原始级别、调用位置和异常信息后转发日志。"""
        try:
            level: str | int = logger.level(record.levelname).name
        except ValueError:
            level = record.levelno

        frame = inspect.currentframe()
        depth = 0
        while frame is not None:
            filename = frame.f_code.co_filename
            is_logging = filename == logging.__file__
            is_frozen_import = (
                "importlib" in filename and "_bootstrap" in filename
            )
            if depth > 0 and not (is_logging or is_frozen_import):
                break
            frame = frame.f_back
            depth += 1

        logger.opt(depth=depth, exception=record.exc_info).log(
            level,
            record.getMessage(),
        )


def setup_logging(settings: Settings) -> None:
    """幂等配置应用日志 sink 并接管标准库日志。"""
    log_file_path = _resolve_log_path(settings.LOG_FILE_PATH)
    error_log_file_path = _resolve_log_path(settings.LOG_ERROR_FILE_PATH)
    if log_file_path == error_log_file_path:
        raise ValueError("普通日志与错误日志文件路径不能相同")

    log_file_path.parent.mkdir(parents=True, exist_ok=True)
    error_log_file_path.parent.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.configure(
        extra={
            "app_name": settings.APP_NAME,
            "run_mode": settings.APP_RUN_MODE,
        }
    )
    try:
        logger.add(
            sys.stderr,
            level=settings.LOG_LEVEL,
            format=_PLAIN_LOG_FORMAT,
            colorize=False if settings.LOG_SERIALIZE else None,
            serialize=settings.LOG_SERIALIZE,
            enqueue=settings.LOG_ENQUEUE,
            backtrace=settings.APP_DEBUG,
            diagnose=False,
        )
        logger.add(
            log_file_path,
            level=settings.LOG_LEVEL,
            format=_PLAIN_LOG_FORMAT,
            filter=_is_normal_record,
            colorize=False,
            serialize=settings.LOG_SERIALIZE,
            enqueue=settings.LOG_ENQUEUE,
            backtrace=settings.APP_DEBUG,
            diagnose=False,
            rotation=settings.LOG_ROTATION,
            retention=settings.LOG_RETENTION,
            encoding="utf-8",
        )
        logger.add(
            error_log_file_path,
            level=_resolve_error_level(settings.LOG_LEVEL),
            format=_PLAIN_LOG_FORMAT,
            colorize=False,
            serialize=settings.LOG_SERIALIZE,
            enqueue=settings.LOG_ENQUEUE,
            backtrace=settings.APP_DEBUG,
            diagnose=False,
            rotation=settings.LOG_ROTATION,
            retention=settings.LOG_RETENTION,
            encoding="utf-8",
        )
    except BaseException:
        logger.remove()
        raise

    intercept_handler = _InterceptHandler()
    logging.basicConfig(
        handlers=[intercept_handler],
        level=logging.NOTSET,
        force=True,
    )
    logging.captureWarnings(True)
    for logger_name in _STANDARD_LOGGER_NAMES:
        standard_logger = logging.getLogger(logger_name)
        standard_logger.handlers.clear()
        standard_logger.addHandler(intercept_handler)
        standard_logger.setLevel(logging.NOTSET)
        standard_logger.propagate = False


__all__ = ["logger", "setup_logging"]
