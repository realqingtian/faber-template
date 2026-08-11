#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : base.py
@Create Time    : 2026-08-11 星期二 23:54:43
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 定义所有持久化文档共享的审计与逻辑删除字段
"""
from datetime import datetime, timezone

from beanie import Insert, Replace, SaveChanges, Update, before_event
from pydantic import BaseModel, Field, field_serializer


DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S"


def _utc_now() -> datetime:
    """返回当前 UTC 时间。"""
    return datetime.now(timezone.utc)


def format_datetime(value: datetime | None) -> str | None:
    """将 MongoDB 时间按 UTC 格式化为年月日时分秒字符串。"""
    if value is None:
        return None
    if value.tzinfo is None:
        value = value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc).strftime(DATETIME_FORMAT)


class BaseDocument(BaseModel):
    """为 Beanie 文档提供统一的审计和逻辑删除字段。"""

    create_date: datetime = Field(default_factory=_utc_now)
    last_modifier_date: datetime | None = None
    created_by: str = "system"
    last_modifier_by: str | None = None
    deleted: bool = False

    @before_event(Insert)
    def initialize_create_date(self) -> None:
        """插入文档前初始化创建时间并清空修改时间。"""
        self.create_date = _utc_now()
        self.last_modifier_date = None

    @before_event(Replace, SaveChanges, Update)
    def refresh_last_modifier_date(self) -> None:
        """更新文档前自动刷新最后修改时间。"""
        self.last_modifier_date = _utc_now()

    @field_serializer(
        "create_date",
        "last_modifier_date",
        when_used="json",
    )
    def serialize_datetime(self, value: datetime | None) -> str | None:
        """将审计时间序列化为统一的年月日时分秒格式。"""
        return format_datetime(value)


__all__ = ["BaseDocument", "DATETIME_FORMAT", "format_datetime"]
