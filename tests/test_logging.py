#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : test_logging.py
@Create Time    : 2026-08-11 星期二 22:00:46
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 验证 Loguru 文本与 JSON 文件日志配置行为
"""
import json
import unittest
from io import StringIO
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import call, patch

from app.core.logging import configure_logging, logger, shutdown_logging
from tests.settings_factory import build_isolated_settings


class LoggingTests(unittest.TestCase):
    def test_plain_text_file_logging_is_enabled_by_default(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            log_file = Path(temporary_directory) / "nested" / "app.log"
            settings = build_isolated_settings(LOG_FILE_PATH=log_file)

            with patch("app.core.logging.sys.stderr", StringIO()):
                handler_ids = configure_logging(settings)
            try:
                logger.info("plain log message")
            finally:
                shutdown_logging(handler_ids)

            log_line = log_file.read_text(encoding="utf-8").strip()

        self.assertFalse(settings.LOG_SERIALIZE)
        self.assertIn("plain log message", log_line)
        with self.assertRaises(json.JSONDecodeError):
            json.loads(log_line)

    def test_serialized_logging_writes_json_record(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            log_file = Path(temporary_directory) / "app.json.log"
            settings = build_isolated_settings(
                LOG_FILE_PATH=log_file,
                LOG_SERIALIZE=True,
            )

            with patch("app.core.logging.sys.stderr", StringIO()):
                handler_ids = configure_logging(settings)
            try:
                logger.bind(request_id="request-123").info(
                    "serialized log message"
                )
            finally:
                shutdown_logging(handler_ids)

            payload = json.loads(log_file.read_text(encoding="utf-8"))

        self.assertEqual(payload["record"]["message"], "serialized log message")
        self.assertEqual(payload["record"]["extra"]["request_id"], "request-123")

    def test_partial_configuration_is_cleaned_up_on_sink_failure(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            settings = build_isolated_settings(
                LOG_FILE_PATH=Path(temporary_directory) / "app.log"
            )

            with (
                patch(
                    "app.core.logging.logger.add",
                    side_effect=[101, OSError("file sink failed")],
                ),
                patch("app.core.logging.logger.remove") as remove,
                self.assertRaisesRegex(OSError, "file sink failed"),
            ):
                configure_logging(settings)

        self.assertEqual(remove.call_args_list, [call(), call(101)])


if __name__ == "__main__":
    unittest.main()
