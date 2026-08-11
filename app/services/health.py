#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : health.py
@Create Time    : 2026-08-11 星期二 20:16:02
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 编排应用外部依赖的健康状态检查
"""
import logging

from app.database import MongoDatabase


logger = logging.getLogger(__name__)


class HealthService:
    """提供不依赖 HTTP 协议的健康检查用例。"""

    def __init__(self, database: MongoDatabase) -> None:
        self._database = database

    async def is_mongodb_ready(self) -> bool:
        """实时检查 MongoDB 是否可响应命令。"""
        try:
            return await self._database.ping()
        except Exception as error:
            logger.warning(
                "MongoDB readiness check failed: %s",
                type(error).__name__,
            )
            return False


__all__ = ["HealthService"]
