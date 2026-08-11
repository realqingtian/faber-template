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
from datetime import date
from typing import Annotated

from beanie import Document, Indexed

from app.models.base import BaseDocument


class User(Document, BaseDocument):
    """保存用户身份资料、密码哈希和启用状态。"""

    user_id: Annotated[
        str,
        Indexed(unique=True),
    ]
    display_id: Annotated[
        str,
        Indexed(unique=True),
    ]
    email: Annotated[
        str,
        Indexed(unique=True),
    ]
    password: str
    nickname: str
    gender: str
    avatar_url: str
    birthday: date
    is_active: int = 0

    class Settings:
        """配置用户文档的 MongoDB 集合。"""

        name = "user"


__all__ = ["User"]
