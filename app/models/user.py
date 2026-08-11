#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : user.py
@Create Time    : 2026-08-11 星期二 23:14:24
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 定义用于身份认证的用户持久化文档
"""
from typing import Annotated

from beanie import Document, Indexed
from pydantic import Field


class User(Document):
    """保存用户身份资料、密码哈希和启用状态。"""

    username: Annotated[
        str,
        Field(min_length=1, max_length=128),
        Indexed(unique=True),
    ]
    email: str | None = Field(default=None, max_length=320)
    full_name: str | None = Field(default=None, max_length=256)
    hashed_password: str = Field(min_length=1)
    disabled: bool = False

    class Settings:
        """配置用户文档的 MongoDB 集合。"""

        name = "users"


__all__ = ["User"]
