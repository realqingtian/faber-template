#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : config.py
@Create Time    : 2026-08-12 星期三 18:56:43
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 配置文件模块
"""
from functools import lru_cache
from pathlib import Path
from typing import Literal, Optional

from pydantic import Field, MongoDsn
from pydantic_settings import BaseSettings, SettingsConfigDict

# 运行模式类型
RUN_MODE_TYPE = Literal['development', 'testing', 'production']

# 根路径
BASE_DIR: Path = Path(__file__).parent.parent.parent
# 环境配置文件
ENV_FILE: Path = BASE_DIR / ".env"


class Settings(BaseSettings):
    """
    应用配置类
    """

    # 模型配置设置
    model_config = SettingsConfigDict(
        env_file=ENV_FILE,  # 环境变量文件路径
        env_file_encoding="utf-8",  # 环境变量文件编码
        case_sensitive=False,  # 是否区分大小写
        env_parse_none_str="null",  # 允许在 .env 中使用 null 表示 None
        extra="ignore",  # 允许 .env 中的配置名称拼写错误被静默忽略
        frozen=True,  # 配置加载后不允许在运行时修改
        str_strip_whitespace=True,  # 去除字符串值首尾空格
    )

    # =============================== 应用配置 ===============================
    RUN_MODE: RUN_MODE_TYPE = Field(
        default='production',
        title='运行模式',
        description='运行模式',
        examples=['development', 'testing', 'production']
    )

    APP_HOST: str = Field(
        default="127.0.0.1",
        title='应用主机',
        description='应用主机',
        examples=['127.0.0.1']
    )
    
    APP_PORT: int = Field(
        default=8000,
        title='应用端口',
        description='应用端口',
        examples=[8000]
    )

    APP_NAME: str = Field(
        default="faber template",
        title='应用名称',
        description='应用名称',
        examples=['faber template']
    )
    APP_DESCRIPTION: str = Field(
        default="一个由 Beanie 和 MongoDB 提供支持的 FastAPI 服务模板",
        title='应用描述',
        description='应用描述',
        examples=['应用描述']
    )
    APP_VERSION: str = Field(
        default="0.1.0",
        title='应用版本',
        description='应用版本',
        examples=['0.1.0']
    )
    APP_API_DOCS_URL: Optional[str] = Field(
        default='/docs',
        title='Swagger UI API 文档地址',
        description='Swagger UI API 文档地址',
        examples=['/docs']
    )
    APP_REDOC_URL: Optional[str] = Field(
        default='/redoc',
        title='ReDoc API 文档地址',
        description='ReDoc API 文档地址',
        examples=['/redoc']
    )
    APP_OPENAPI_URL: Optional[str] = Field(
        default='/openapi.json',
        title='OpenAPI JSON 文件地址',
        description='OpenAPI JSON 文件地址',
        examples=['/openapi.json']
    )
    APP_DEBUG: bool = Field(
        default=False,
        title='应用调试模式',
        description='应用调试模式',
        examples=[False]
    )
    APP_RELOAD: bool = Field(
        default=False,
        title='应用重载模式',
        description='应用重载模式',
        examples=[False]
    )

    # =============================== MongoDB配置 ===============================
    MONGODB_URI: MongoDsn = Field(
        default=MongoDsn('mongodb://localhost:27017?authSource=admin'),
        title='MongoDB 连接字符串',
        description='MongoDB 连接字符串',
        examples=['mongodb://localhost:27017/faber_template?authSource=admin']
    )

    MONGODB_NAME: str = Field(
        default="faber_template",
        title='MongoDB 数据库名称',
        description='MongoDB 数据库名称',
        examples=['faber_template']
    )

    MONGODB_SERVER_SELECTION_TIMEOUT_MS: int = Field(
        default=1000,
        title='MongoDB 服务器选择超时时间',
        description='MongoDB 服务器选择超时时间',
        examples=[1000]
    )

    # =============================== 跨域配置 ===============================
    CORS_ORIGINS_LIST: str = Field(
        default="*",
        title='跨域允许的来源',
        description='跨域允许的来源 默认允许所有来源 可以使用逗号分隔的列表，例如: https://example.com,https://example.org',
        examples=['*']
    )

    # =============================== JWT配置 ===============================
    JWT_SECRET_KEY: str = Field(
        default="Y0uSh0uldCh4ng3Th1sSecretK3y!",
        title='密钥',
        description='密钥',
        examples=['使用 openssl rand -hex 32 生成']
    )
    JWT_ALGORITHM: str = Field(
        default="HS256",
        title='算法',
        description='算法',
        examples=['HS256']
    )
    JWT_ACCESS_TOKEN_EXPIRE_DAYS: int = Field(
        default=30,
        title='访问令牌过期时间',
        description='访问令牌过期时间',
        examples=[30]
    )
    JWT_REFRESH_TOKEN_EXPIRE_DAYS: int = Field(
        default=180,
        title='刷新令牌过期时间',
        description='刷新令牌过期时间',
        examples=[180]
    )

    # =============================== 日志配置 ===============================
    LOG_LEVEL: str = Field(
        default="INFO",
        title='日志级别',
        description='日志级别',
        examples=['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']
    )

    LOG_SERIALIZE: bool = Field(
        default=True,
        title='日志序列化',
        description='日志序列化',
        examples=[True]
    )

    LOG_OUTPUT_FILE: bool = Field(
        default=True,
        title='日志输出文件',
        description='日志输出文件',
        examples=[True]
    )

    LOG_ROTATION: str = Field(
        default='10 MB',
        title='日志轮转',
        description='日志轮转',
        examples=['10 MB']
    )

    LOG_RETENTION: str = Field(
        default='30 days',
        title='日志保留天数',
        description='日志保留天数',
        examples=['30 days']
    )

    ACCESS_LOG_FILE: str = Field(
        default="access_%Y%m%d.log",
        title='访问日志文件名',
        description='访问日志文件名',
        examples=['app_20230812.log']
    )

    ERROR_LOG_FILE: str = Field(
        default="error_%Y%m%d.log",
        title='错误日志文件名',
        description='错误日志文件名',
        examples=['app_20230812.log']
    )

    LOG_DIR: Path = Field(
        default=BASE_DIR / 'logs',
        title='日志目录',
        description='日志目录',
        examples=['logs']
    )


class DevelopmentSettings(Settings):
    """
    开发环境配置类
    """

    RUN_MODE: RUN_MODE_TYPE = Field(
        default='development',
        title='运行模式',
        description='运行模式',
        examples=['development']
    )

    APP_DEBUG: bool = Field(
        default=True,
        title='应用调试模式',
        description='应用调试模式',
        examples=[True]
    )

    APP_RELOAD: bool = Field(
        default=True,
        title='应用重载模式',
        description='应用重载模式',
        examples=[True]
    )


class TestingSettings(Settings):
    """
    测试环境配置类
    """

    RUN_MODE: RUN_MODE_TYPE = Field(
        default='testing',
        title='运行模式',
        description='运行模式',
        examples=['testing']
    )

    APP_DEBUG: bool = Field(
        default=False,
        title='应用调试模式',
        description='应用调试模式',
        examples=[False]
    )

    APP_RELOAD: bool = Field(
        default=False,
        title='应用重载模式',
        description='应用重载模式',
        examples=[False]
    )


class ProductionSettings(Settings):
    """
    生产环境配置类
    """

    RUN_MODE: RUN_MODE_TYPE = Field(
        default='production',
        title='运行模式',
        description='运行模式',
        examples=['production']
    )

    APP_DEBUG: bool = Field(
        default=False,
        title='应用调试模式',
        description='应用调试模式',
        examples=[False]
    )

    APP_RELOAD: bool = Field(
        default=False,
        title='应用重载模式',
        description='应用重载模式',
        examples=[False]
    )


class _EnvironmentSelector(BaseSettings):
    """
    仅用于读取当前运行环境
    """

    model_config = SettingsConfigDict(env_file=ENV_FILE, extra="ignore")

    RUN_MODE: RUN_MODE_TYPE = "development"


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    获取应用配置
    """
    mode = _EnvironmentSelector().RUN_MODE

    settings_map: dict[RUN_MODE_TYPE, type[Settings]] = {
        "development": DevelopmentSettings,
        "testing": TestingSettings,
        "production": ProductionSettings,
    }

    settings_class = settings_map[mode]

    return settings_class()


if __name__ == '__main__':
    settings_obj = get_settings()
    print(settings_obj.model_dump())
