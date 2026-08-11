#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : test_mongodb.py
@Create Time    : 2026-08-11 星期二 17:08:01
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : MongoDB 连接管理模块的单元测试
"""

import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from app.database.mongodb import MongoDatabase
from tests.settings_factory import build_isolated_settings


class MongoDatabaseTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.settings = build_isolated_settings(
            MONGODB_URI="mongodb://mongo.example:27017",
            MONGODB_DATABASE="test_database",
            MONGODB_SERVER_SELECTION_TIMEOUT_MS=1234,
        )

    async def test_connect_pings_and_initializes_beanie(self) -> None:
        client = MagicMock()
        client.close = AsyncMock()
        database = MagicMock()
        database.command = AsyncMock(return_value={"ok": 1})
        client.__getitem__.return_value = database

        with (
            patch("app.database.mongodb.AsyncMongoClient", return_value=client) as client_class,
            patch("app.database.mongodb.init_beanie", new=AsyncMock()) as init_beanie,
        ):
            manager = MongoDatabase()
            result = await manager.connect(self.settings, document_models=[])

        self.assertIs(result, database)
        self.assertTrue(manager.is_connected)
        client_class.assert_called_once_with(
            self.settings.MONGODB_URI,
            serverSelectionTimeoutMS=1234,
        )
        client.__getitem__.assert_called_once_with("test_database")
        database.command.assert_awaited_once_with("ping")
        init_beanie.assert_awaited_once_with(
            database=database,
            document_models=[],
        )

    async def test_connect_is_idempotent(self) -> None:
        client = MagicMock()
        client.close = AsyncMock()
        database = MagicMock()
        database.command = AsyncMock(return_value={"ok": 1})
        client.__getitem__.return_value = database

        with (
            patch("app.database.mongodb.AsyncMongoClient", return_value=client) as client_class,
            patch("app.database.mongodb.init_beanie", new=AsyncMock()),
        ):
            manager = MongoDatabase()
            first = await manager.connect(self.settings, document_models=[])
            second = await manager.connect(self.settings, document_models=[])

        self.assertIs(first, second)
        client_class.assert_called_once()

    async def test_failed_initialization_closes_client(self) -> None:
        client = MagicMock()
        client.close = AsyncMock()
        database = MagicMock()
        database.command = AsyncMock(return_value={"ok": 1})
        client.__getitem__.return_value = database

        with (
            patch("app.database.mongodb.AsyncMongoClient", return_value=client),
            patch(
                "app.database.mongodb.init_beanie",
                new=AsyncMock(side_effect=RuntimeError("initialization failed")),
            ),
        ):
            manager = MongoDatabase()
            with self.assertRaisesRegex(RuntimeError, "initialization failed"):
                await manager.connect(self.settings, document_models=[])

        client.close.assert_awaited_once()
        self.assertFalse(manager.is_connected)

    async def test_ping_and_disconnect(self) -> None:
        client = MagicMock()
        client.close = AsyncMock()
        database = MagicMock()
        database.command = AsyncMock(side_effect=[{"ok": 1}, {"ok": 1}])
        client.__getitem__.return_value = database

        with (
            patch("app.database.mongodb.AsyncMongoClient", return_value=client),
            patch("app.database.mongodb.init_beanie", new=AsyncMock()),
        ):
            manager = MongoDatabase()
            await manager.connect(self.settings, document_models=[])
            self.assertTrue(await manager.ping())
            await manager.disconnect()

        client.close.assert_awaited_once()
        self.assertFalse(manager.is_connected)
        with self.assertRaisesRegex(RuntimeError, "MongoDB 尚未连接"):
            _ = manager.database


if __name__ == "__main__":
    unittest.main()
