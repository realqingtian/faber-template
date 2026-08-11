#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : config.py
@Create Time    : 2026-08-11 星期二 17:19:07
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 定义并缓存按运行环境选择的应用配置
"""
from functools import lru_cache
from pathlib import Path
from typing import Literal

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict


PROJECT_ROOT = Path(__file__).resolve().parents[2]
ENV_FILE = PROJECT_ROOT / ".env"
RunMode = Literal["development", "testing", "production"]
LogLevel = Literal[
    "TRACE",
    "DEBUG",
    "INFO",
    "SUCCESS",
    "WARNING",
    "ERROR",
    "CRITICAL",
]


class Settings(BaseSettings):
    """应用公共配置。"""

    # 模型配置设置
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,  # 环境变量文件路径
        env_file_encoding="utf-8",  # 环境变量文件编码
        case_sensitive=False,  # 是否区分大小写
        env_parse_none_str="null",  # 允许在 .env 中使用 null 表示 None
        extra="forbid",  # 防止 .env 中的配置名称拼写错误被静默忽略
        frozen=True,  # 配置加载后不允许在运行时修改
        str_strip_whitespace=True,  # 去除字符串值首尾空格
    )

    # ========================= 基础配置 =========================
    APP_NAME: str = Field(default="faber-template", min_length=1, title="应用名称")
    APP_DESCRIPTION: str = Field(
        default="一个由 Beanie 和 MongoDB 提供支持的 FastAPI 服务模板",
        title="应用描述",
    )
    APP_VERSION: str = Field(default="0.1.0", min_length=1, title="应用版本")
    APP_RUN_MODE: RunMode = Field(default="production", title="应用运行模式")
    APP_HOST: str = Field(default="127.0.0.1", min_length=1, title="应用主机")
    APP_PORT: int = Field(default=8000, ge=1, le=65535, title="应用端口")
    APP_DEBUG: bool = Field(default=False, title="应用 Debug")
    APP_API_DOCS: str | None = Field(default=None, title="Swagger UI 路径")
    APP_API_REDOC: str | None = Field(default=None, title="ReDoc 路径")
    APP_API_OPENAPI: str | None = Field(default=None, title="OpenAPI 路径")

    # ========================= 日志配置 =========================
    LOG_LEVEL: LogLevel = Field(default="INFO", title="日志最低级别")
    LOG_FILE_PATH: Path = Field(
        default=PROJECT_ROOT / "logs" / "app.log",
        title="普通日志文件路径",
    )
    LOG_ERROR_FILE_PATH: Path = Field(
        default=PROJECT_ROOT / "logs" / "error.log",
        title="错误日志文件路径",
    )
    LOG_SERIALIZE: bool = Field(
        default=False,
        title="是否输出 JSON 序列化结构日志",
    )
    LOG_ENQUEUE: bool = Field(
        default=True,
        title="是否通过队列异步安全写入日志",
    )
    LOG_ROTATION: str | None = Field(
        default="10 MB",
        min_length=1,
        title="日志文件轮转条件",
    )
    LOG_RETENTION: str | None = Field(
        default="30 days",
        min_length=1,
        title="历史日志保留期限",
    )

    # ========================= MongoDB配置 =========================
    MONGODB_URI: str = Field(
        default="mongodb://127.0.0.1:27017",
        min_length=1,
        title="MongoDB 连接 URI",
    )
    MONGODB_DATABASE: str = Field(
        default="faber-template",
        min_length=1,
        title="MongoDB 数据库名称",
    )
    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = Field(
        default=5000,
        gt=0,
        title="MongoDB 服务器选择超时时间（毫秒）",
    )


class DevelopmentSettings(Settings):
    """开发环境默认配置。"""

    APP_RUN_MODE: Literal["development"] = "development"
    APP_DEBUG: bool = True


class TestingSettings(Settings):
    """测试环境默认配置。"""

    APP_RUN_MODE: Literal["testing"] = "testing"
    APP_DEBUG: bool = False


class ProductionSettings(Settings):
    """生产环境默认配置。"""

    APP_RUN_MODE: Literal["production"] = "production"
    APP_DEBUG: bool = False


class _EnvironmentSelector(BaseSettings):
    """只读取运行模式，用于选择对应的完整配置类。"""

    model_config = SettingsConfigDict(
        env_file=ENV_FILE,  # 环境变量文件路径
        env_file_encoding="utf-8",  # 环境变量文件编码
        case_sensitive=False,  # 是否区分大小写
        extra="ignore",  # 忽略 .env 中未定义的配置名称
    )

    APP_RUN_MODE: RunMode = "development"


_SETTINGS_BY_RUN_MODE: dict[RunMode, type[Settings]] = {
    "development": DevelopmentSettings,
    "testing": TestingSettings,
    "production": ProductionSettings,
}


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """读取并缓存当前运行环境对应的配置。"""
    run_mode = _EnvironmentSelector().APP_RUN_MODE
    settings_class = _SETTINGS_BY_RUN_MODE[run_mode]
    return settings_class()


if __name__ == '__main__':
    config_field = get_settings()
    print(config_field.model_dump())
