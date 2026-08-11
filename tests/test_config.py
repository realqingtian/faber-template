import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from unittest.mock import patch

from pydantic import ValidationError

from app.core.config import (
    DevelopmentSettings,
    ProductionSettings,
    Settings,
    TestingSettings,
    get_settings,
)
from tests.settings_factory import (
    build_isolated_settings,
    load_settings_from_env_file,
)


class SettingsTests(unittest.TestCase):
    def tearDown(self) -> None:
        get_settings.cache_clear()

    def test_env_file_is_loaded_outside_project_directory(self) -> None:
        original_directory = Path.cwd()
        with (
            TemporaryDirectory() as environment_directory,
            TemporaryDirectory() as working_directory,
        ):
            env_file = Path(environment_directory) / ".env"
            env_file.write_text(
                "APP_NAME=dotenv-name\n"
                "MONGODB_URI=mongodb://dotenv.example:27017\n",
                encoding="utf-8",
            )
            with patch.dict(os.environ, {}, clear=True):
                try:
                    os.chdir(working_directory)
                    settings = load_settings_from_env_file(env_file)
                finally:
                    os.chdir(original_directory)

        self.assertIn("APP_NAME", settings.model_fields_set)
        self.assertIn("MONGODB_URI", settings.model_fields_set)
        self.assertEqual(settings.APP_NAME, "dotenv-name")
        self.assertEqual(settings.MONGODB_URI, "mongodb://dotenv.example:27017")

    def test_get_settings_selects_configuration_by_run_mode(self) -> None:
        expected_types = {
            "development": DevelopmentSettings,
            "testing": TestingSettings,
            "production": ProductionSettings,
        }

        for run_mode, expected_type in expected_types.items():
            with self.subTest(run_mode=run_mode):
                with patch.dict(os.environ, {"APP_RUN_MODE": run_mode}):
                    get_settings.cache_clear()
                    settings = get_settings()

                self.assertIsInstance(settings, expected_type)
                self.assertEqual(settings.APP_RUN_MODE, run_mode)

    def test_system_environment_overrides_env_file(self) -> None:
        with patch.dict(
            os.environ,
            {"APP_NAME": "environment-name", "APP_DEBUG": "true"},
        ):
            settings = Settings()

        self.assertEqual(settings.APP_NAME, "environment-name")
        self.assertTrue(settings.APP_DEBUG)

    def test_get_settings_reuses_cached_instance(self) -> None:
        self.assertIs(get_settings(), get_settings())

    def test_unknown_dotenv_key_is_rejected(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            env_file = Path(temporary_directory) / ".env"
            env_file.write_text("UNKNOWN_SETTING=value\n", encoding="utf-8")

            with self.assertRaises(ValidationError):
                load_settings_from_env_file(env_file)

    def test_document_path_must_start_with_slash(self) -> None:
        for field_name in ("APP_API_DOCS", "APP_API_REDOC", "APP_API_OPENAPI"):
            with self.subTest(field_name=field_name):
                with self.assertRaises(ValidationError):
                    build_isolated_settings(**{field_name: "invalid-path"})

    def test_port_must_be_in_tcp_range(self) -> None:
        for port in (0, 65536):
            with self.subTest(port=port):
                with self.assertRaises(ValidationError):
                    build_isolated_settings(APP_PORT=port)

    def test_null_disables_document_path(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            env_file = Path(temporary_directory) / ".env"
            env_file.write_text("APP_API_DOCS=null\n", encoding="utf-8")
            settings = load_settings_from_env_file(env_file)

        self.assertIsNone(settings.APP_API_DOCS)

    def test_log_serialization_is_disabled_by_default(self) -> None:
        settings = build_isolated_settings()

        self.assertFalse(settings.LOG_SERIALIZE)

    def test_log_serialization_can_be_enabled_from_env_file(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            env_file = Path(temporary_directory) / ".env"
            env_file.write_text("LOG_SERIALIZE=true\n", encoding="utf-8")
            settings = load_settings_from_env_file(env_file)

        self.assertTrue(settings.LOG_SERIALIZE)

    def test_relative_log_file_path_is_resolved_from_project_root(self) -> None:
        settings = build_isolated_settings(LOG_FILE_PATH="var/log/app.log")

        self.assertTrue(settings.LOG_FILE_PATH.is_absolute())
        self.assertEqual(
            settings.LOG_FILE_PATH.parts[-3:],
            ("var", "log", "app.log"),
        )

    def test_unknown_log_level_is_rejected(self) -> None:
        with self.assertRaises(ValidationError):
            build_isolated_settings(LOG_LEVEL="VERBOSE")


if __name__ == "__main__":
    unittest.main()
