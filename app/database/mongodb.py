#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : mongodb.py
@Create Time    : 2026-08-11 星期二 17:08:01
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : MongoDB 异步连接、Beanie 初始化与连接生命周期管理
"""
from typing import AsyncIterator
from collections.abc import Sequence
from contextlib import asynccontextmanager


from beanie import Document, init_beanie
from pymongo.asynchronous.database import AsyncDatabase
from pymongo.asynchronous.mongo_client import AsyncMongoClient

from app.models import DOCUMENT_MODELS
from app.core.config import Settings, get_settings


class MongoDatabase:
    """管理单个 MongoDB 客户端及其 Beanie 初始化状态。"""

    def __init__(self) -> None:
        self._client: AsyncMongoClient | None = None
        self._database: AsyncDatabase | None = None

    @property
    def client(self) -> AsyncMongoClient:
        """返回已连接的 MongoDB 客户端。"""
        if self._client is None:
            raise RuntimeError("MongoDB 尚未连接")
        return self._client

    @property
    def database(self) -> AsyncDatabase:
        """返回已初始化的 MongoDB 数据库。"""
        if self._database is None:
            raise RuntimeError("MongoDB 尚未连接")
        return self._database

    @property
    def is_connected(self) -> bool:
        """返回当前进程是否已完成数据库初始化。"""
        return self._client is not None and self._database is not None

    async def connect(
        self,
        settings: Settings | None = None,
        document_models: Sequence[type[Document] | str] = DOCUMENT_MODELS,
    ) -> AsyncDatabase:
        """连接 MongoDB、执行探活并初始化 Beanie。"""
        if self.is_connected:
            return self.database

        config = settings or get_settings()
        client = AsyncMongoClient(
            config.MONGODB_URI,
            serverSelectionTimeoutMS=config.MONGODB_SERVER_SELECTION_TIMEOUT_MS,
        )
        database = client[config.MONGODB_DATABASE]

        try:
            # AsyncMongoClient 是惰性连接，ping 用于在应用启动时快速暴露配置或网络错误。
            await database.command("ping")
            await init_beanie(
                database=database,
                document_models=document_models,
            )
        except BaseException:
            await client.close()
            raise

        self._client = client
        self._database = database
        return database

    async def ping(self) -> bool:
        """检查已建立的 MongoDB 连接是否可用。"""
        result = await self.database.command("ping")
        return result.get("ok") == 1

    async def disconnect(self) -> None:
        """关闭 MongoDB 客户端并清理本地状态。"""
        client = self._client
        self._client = None
        self._database = None

        if client is not None:
            await client.close()


mongodb = MongoDatabase()


async def connect_to_mongodb() -> AsyncDatabase:
    """使用应用配置初始化全局 MongoDB 连接。"""
    return await mongodb.connect()


async def close_mongodb_connection() -> None:
    """关闭全局 MongoDB 连接。"""
    await mongodb.disconnect()


@asynccontextmanager
async def mongodb_lifespan() -> AsyncIterator[MongoDatabase]:
    """为应用生命周期提供可组合的 MongoDB 上下文。"""
    await mongodb.connect()
    try:
        yield mongodb
    finally:
        await mongodb.disconnect()


__all__ = [
    "MongoDatabase",
    "close_mongodb_connection",
    "connect_to_mongodb",
    "mongodb",
    "mongodb_lifespan",
]
