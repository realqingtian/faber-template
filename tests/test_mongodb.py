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
from datetime import date, datetime, timezone
from unittest.mock import AsyncMock, MagicMock, patch

from beanie import Insert, Replace, SaveChanges, Update
from app.core.security import DUMMY_PASSWORD_HASH
from app.database.mongodb import MongoDatabase
from app.models import BaseDocument, DOCUMENT_MODELS, User
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

    def test_user_document_is_registered_with_unique_identity_indexes(self) -> None:
        self.assertIn(User, DOCUMENT_MODELS)

        for field_name in ("user_id", "display_id", "email"):
            with self.subTest(field_name=field_name):
                index_metadata = next(
                    metadata
                    for metadata in User.model_fields[field_name].metadata
                    if hasattr(metadata, "_indexed")
                )
                self.assertEqual(
                    index_metadata._indexed[1],
                    {"unique": True},
                )


class BaseDocumentTests(unittest.TestCase):
    def test_base_fields_receive_non_null_safe_defaults(self) -> None:
        document = BaseDocument()

        self.assertIsNotNone(document.create_date.tzinfo)
        self.assertIsNone(document.last_modifier_date)
        self.assertEqual(document.created_by, "system")
        self.assertIsNone(document.last_modifier_by)
        self.assertFalse(document.deleted)

    def test_insert_and_update_hooks_refresh_audit_dates(self) -> None:
        document = BaseDocument()
        created_at = datetime(2026, 8, 11, 10, 20, 30, tzinfo=timezone.utc)
        modified_at = datetime(2026, 8, 12, 1, 2, 3, tzinfo=timezone.utc)

        with patch(
            "app.models.base._utc_now",
            side_effect=[created_at, modified_at],
        ):
            document.initialize_create_date()
            document.refresh_last_modifier_date()

        self.assertEqual(document.create_date, created_at)
        self.assertEqual(document.last_modifier_date, modified_at)

    def test_user_inherits_beanie_audit_event_hooks(self) -> None:
        self.assertEqual(User.initialize_create_date.event_types, [Insert])
        self.assertEqual(
            User.refresh_last_modifier_date.event_types,
            [Replace, SaveChanges, Update],
        )

    def test_audit_dates_are_formatted_as_utc_for_json(self) -> None:
        document = BaseDocument(
            create_date=datetime(2026, 8, 11, 10, 20, 30),
            last_modifier_date=datetime(
                2026,
                8,
                11,
                18,
                20,
                30,
                tzinfo=timezone.utc,
            ),
        )

        payload = document.model_dump(mode="json")

        self.assertEqual(payload["create_date"], "2026-08-11 10:20:30")
        self.assertEqual(
            payload["last_modifier_date"],
            "2026-08-11 18:20:30",
        )

    def test_user_declares_required_profile_fields_and_defaults(self) -> None:
        required_fields = {
            "user_id",
            "display_id",
            "email",
            "password",
            "nickname",
            "gender",
            "avatar_url",
            "birthday",
        }

        self.assertTrue(
            all(User.model_fields[field].is_required() for field in required_fields)
        )
        self.assertEqual(User.model_fields["is_active"].default, 0)

        with patch.object(User, "get_pymongo_collection"):
            user = User(
                user_id="1234567890",
                email="john@example.com",
                display_id="0987654321",
                password=DUMMY_PASSWORD_HASH,
                nickname="John Doe",
                gender="male",
                avatar_url="https://example.com/avatar.png",
                birthday=date(2000, 1, 2),
            )
        self.assertEqual(user.email, "john@example.com")

    def test_user_collection_does_not_apply_request_validation_rules(self) -> None:
        with patch.object(User, "get_pymongo_collection"):
            user = User(
                user_id="not-ten-digits",
                display_id="display-value",
                email="not-an-email",
                password="request-layer-validates-this",
                nickname="",
                gender="",
                avatar_url="not-a-url",
                birthday=date(2000, 1, 2),
                is_active=7,
            )

        self.assertEqual(user.user_id, "not-ten-digits")
        self.assertEqual(user.email, "not-an-email")
        self.assertEqual(user.password, "request-layer-validates-this")
        self.assertEqual(user.is_active, 7)
        self.assertEqual(User.model_fields["password"].metadata, [])


if __name__ == "__main__":
    unittest.main()
