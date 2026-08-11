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


class SettingsTests(unittest.TestCase):
    def tearDown(self) -> None:
        get_settings.cache_clear()

    def test_env_file_is_loaded_outside_project_directory(self) -> None:
        original_directory = Path.cwd()
        with TemporaryDirectory() as temporary_directory:
            try:
                os.chdir(temporary_directory)
                settings = Settings()
            finally:
                os.chdir(original_directory)

        self.assertIn("APP_NAME", settings.model_fields_set)
        self.assertIn("MONGODB_URI", settings.model_fields_set)

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
                Settings(_env_file=env_file)

    def test_document_path_must_start_with_slash(self) -> None:
        with self.assertRaises(ValidationError):
            Settings(_env_file=None, APP_API_DOCS="docs")

    def test_null_disables_document_path(self) -> None:
        with TemporaryDirectory() as temporary_directory:
            env_file = Path(temporary_directory) / ".env"
            env_file.write_text("APP_API_DOCS=null\n", encoding="utf-8")
            settings = Settings(_env_file=env_file)

        self.assertIsNone(settings.APP_API_DOCS)


if __name__ == "__main__":
    unittest.main()
