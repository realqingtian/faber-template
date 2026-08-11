#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : settings_factory.py
@Create Time    : 2026-08-11 星期二 20:41:55
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 为单元测试构造具有可控 dotenv 来源的应用配置
"""

from pathlib import Path
from typing import Any

from pydantic import Field, SecretStr
from pydantic_settings import SettingsConfigDict

from app.core.config import Settings


TEST_JWT_SECRET_KEY = "test-only-jwt-secret-key-32-characters"


class _IsolatedSettings(Settings):
    """不读取项目 dotenv 文件的测试配置。"""

    model_config = SettingsConfigDict(env_file=None)
    JWT_SECRET_KEY: SecretStr = Field(
        default=SecretStr(TEST_JWT_SECRET_KEY),
        min_length=32,
    )


def build_isolated_settings(**overrides: Any) -> Settings:
    """构造不读取项目 dotenv 文件的测试配置。"""
    return _IsolatedSettings(**overrides)


def load_settings_from_env_file(env_file: Path) -> Settings:
    """仅从指定 dotenv 文件构造测试配置。"""

    class _EnvFileSettings(Settings):
        model_config = SettingsConfigDict(env_file=env_file)
        JWT_SECRET_KEY: SecretStr = Field(
            default=SecretStr(TEST_JWT_SECRET_KEY),
            min_length=32,
        )

    return _EnvFileSettings()


__all__ = [
    "TEST_JWT_SECRET_KEY",
    "build_isolated_settings",
    "load_settings_from_env_file",
]
