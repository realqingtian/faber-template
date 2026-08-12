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
import sys

from loguru import logger

from app.core.config import get_settings


settings = get_settings()

_LOG_FORMAT = (
    "<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | "
    "<level>{level: <8}</level> | "
    "<magenta>[{extra[request_id]}]</magenta> | "
    "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
    "<level>{message}</level>"
)


def setup_logger(
    log_level: str = settings.LOG_LEVEL,  # 日志级别
    retention: str = settings.LOG_RETENTION,  # 日志保留时间
    rotation: str = settings.LOG_ROTATION,  # 日志切割时间
    serialize: bool = settings.LOG_SERIALIZE,  # 是否序列化日志
    backtrace: bool = True,  # 是否启用回溯
) -> None:
    """
    生产环境推荐配置
    :param log_level: 日志级别
    :param retention: 日志保留时间
    :param rotation: 日志切割时间
    :param serialize: 是否序列化日志
    :param backtrace: 是否启用回溯
    :return: None
    """
    # 移除默认的控制台输出
    logger.remove()

    # 只有开发环境才启用诊断，生产环境禁用
    is_diagnose = False if settings.RUN_MODE.lower() == 'production' else True

    # 控制台输出
    logger.add(
        sys.stdout,  # 控制台输出
        format=_LOG_FORMAT,  # 日志格式
        level=log_level,  # 日志级别
        backtrace=backtrace,  # 是否启用回溯
        serialize=serialize,  # 是否序列化日志
        diagnose=is_diagnose,  # 是否启用诊断
    )

    # 日志是否输出到文件
    if settings.LOG_OUTPUT_FILE:
        # 全部日志文件
        logger.add(
            settings.LOG_DIR / "app_{time:YYYY-MM-DD}.log",  # 日志文件路径
            format=_LOG_FORMAT,  # 日志格式
            level=log_level,  # 日志级别
            rotation=rotation,  # 日志切割时间
            retention=retention,  # 日志保留时间
            encoding="utf-8",  # 日志编码
            serialize=serialize,  # 是否序列化日志
            backtrace=backtrace,  # 是否启用回溯
            diagnose=is_diagnose,  # 是否启用诊断
        )

        # 错误日志单独文件
        logger.add(
            settings.LOG_DIR / "error_{time:YYYY-MM-DD}.log",  # 日志文件路径
            format=_LOG_FORMAT,  # 日志格式
            level="ERROR",  # 日志级别
            rotation=rotation,  # 日志切割时间
            retention=retention,  # 日志保留时间
            encoding="utf-8",  # 日志编码
            serialize=serialize,  # 是否序列化日志
            backtrace=backtrace,  # 是否启用回溯
            diagnose=is_diagnose,  # 是否启用诊断
        )

    # 默认 extra
    logger.configure(extra={"request_id": "N/A"})


# 默认初始化
setup_logger()

__all__ = ["logger", "setup_logger"]


if __name__ == '__main__':
    logger.info('INFO 信息')