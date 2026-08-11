#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : users.py
@Create Time    : 2026-08-11 星期二 23:14:24
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 封装用户身份数据的 Beanie 查询
"""
from app.models import User


class UserRepository:
    """提供认证流程所需的用户数据访问能力。"""

    async def get_by_username(self, username: str) -> User | None:
        """按唯一用户名查询用户。"""
        return await User.find_one(User.username == username)


__all__ = ["UserRepository"]
