#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : auth.py
@Create Time    : 2026-08-11 星期二 23:14:24
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 编排用户密码认证与 JWT 身份解析流程
"""
import asyncio
from datetime import timedelta

from app.core.config import Settings
from app.core.security import (
    DUMMY_PASSWORD_HASH,
    create_access_token,
    decode_access_token,
    verify_password,
)
from app.models import User
from app.repositories import UserRepository


class AuthService:
    """提供不依赖 HTTP 协议的认证用例。"""

    def __init__(self, repository: UserRepository, settings: Settings) -> None:
        self._repository = repository
        self._settings = settings

    async def authenticate(self, username: str, password: str) -> User | None:
        """校验用户凭据，失败时返回 None。"""
        user = await self._repository.get_by_username(username)
        password_hash = (
            user.hashed_password if user is not None else DUMMY_PASSWORD_HASH
        )
        password_matches = await asyncio.to_thread(
            verify_password,
            password,
            password_hash,
        )
        if user is None or not password_matches:
            return None
        return user

    def issue_access_token(self, user: User) -> str:
        """为已认证用户签发配置时长的访问令牌。"""
        return create_access_token(
            subject=user.username,
            secret_key=self._settings.JWT_SECRET_KEY.get_secret_value(),
            algorithm=self._settings.JWT_ALGORITHM,
            expires_delta=timedelta(
                minutes=self._settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES
            ),
        )

    async def resolve_user(self, token: str) -> User | None:
        """验证访问令牌并查询其当前用户。"""
        username = decode_access_token(
            token,
            secret_key=self._settings.JWT_SECRET_KEY.get_secret_value(),
            algorithm=self._settings.JWT_ALGORITHM,
        )
        return await self._repository.get_by_username(username)


__all__ = ["AuthService"]
