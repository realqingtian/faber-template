#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : test_app.py
@Create Time    : 2026-08-11 星期二 20:16:03
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : FastAPI 应用生命周期与健康检查端点的单元测试
"""
import unittest
from unittest.mock import AsyncMock, MagicMock, patch

from fastapi.testclient import TestClient

from app.app_factory import create_app
from app.core.config import get_settings
from app.database import MongoDatabase


class AppFactoryTests(unittest.TestCase):
    def setUp(self) -> None:
        get_settings.cache_clear()
        self.database = MagicMock(spec=MongoDatabase)
        self.database.connect = AsyncMock()
        self.database.disconnect = AsyncMock()
        self.database.ping = AsyncMock(return_value=True)
        self.logging_handler_ids = (101, 102)
        self.configure_logging_patcher = patch(
            "app.core.lifespan.configure_logging",
            return_value=self.logging_handler_ids,
        )
        self.shutdown_logging_patcher = patch(
            "app.core.lifespan.shutdown_logging"
        )
        self.log_info_patcher = patch("app.core.lifespan.logger.info")
        self.configure_logging = self.configure_logging_patcher.start()
        self.shutdown_logging = self.shutdown_logging_patcher.start()
        self.log_info = self.log_info_patcher.start()

    def tearDown(self) -> None:
        self.log_info_patcher.stop()
        self.shutdown_logging_patcher.stop()
        self.configure_logging_patcher.stop()
        get_settings.cache_clear()

    def test_lifespan_connects_and_disconnects_database(self) -> None:
        app = create_app()

        with patch("app.core.lifespan.mongodb", self.database):
            with TestClient(app) as client:
                self.assertIs(app.state.mongodb, self.database)
                self.assertEqual(client.get("/health/live").status_code, 200)

        self.database.connect.assert_awaited_once_with()
        self.database.disconnect.assert_awaited_once_with()
        self.configure_logging.assert_called_once_with(get_settings())
        self.shutdown_logging.assert_called_once_with(self.logging_handler_ids)

    def test_startup_fails_when_database_connection_fails(self) -> None:
        self.database.connect.side_effect = RuntimeError("connection failed")
        app = create_app()

        with patch("app.core.lifespan.mongodb", self.database):
            with self.assertRaisesRegex(RuntimeError, "connection failed"):
                with TestClient(app):
                    self.fail("数据库连接失败时不应进入应用生命周期")

        self.database.disconnect.assert_not_awaited()
        self.shutdown_logging.assert_called_once_with(self.logging_handler_ids)

    def test_liveness_does_not_query_database(self) -> None:
        with patch("app.core.lifespan.mongodb", self.database):
            with TestClient(create_app()) as client:
                response = client.get("/health/live")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"status": "ok"})
        self.database.ping.assert_not_awaited()

    def test_readiness_reports_available_database(self) -> None:
        with patch("app.core.lifespan.mongodb", self.database):
            with TestClient(create_app()) as client:
                response = client.get("/health/ready")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"status": "ready", "checks": {"mongodb": "up"}},
        )
        self.database.ping.assert_awaited_once_with()

    def test_readiness_returns_503_when_ping_is_unsuccessful(self) -> None:
        self.database.ping.return_value = False

        with patch("app.core.lifespan.mongodb", self.database):
            with TestClient(create_app()) as client:
                response = client.get("/health/ready")

        self.assertEqual(response.status_code, 503)
        self.assertEqual(
            response.json(),
            {"status": "not_ready", "checks": {"mongodb": "down"}},
        )

    def test_readiness_hides_database_exception_details(self) -> None:
        self.database.ping.side_effect = RuntimeError(
            "mongodb://username:password@mongo.example/internal"
        )

        with (
            patch("app.core.lifespan.mongodb", self.database),
            patch("app.services.health.logger.warning") as warning,
        ):
            with TestClient(create_app()) as client:
                response = client.get("/health/ready")

        self.assertEqual(response.status_code, 503)
        self.assertNotIn("username", response.text)
        warning.assert_called_once_with(
            "MongoDB readiness check failed: {}",
            "RuntimeError",
        )
        self.assertNotIn("password", repr(warning.call_args))


if __name__ == "__main__":
    unittest.main()
