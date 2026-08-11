#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : security.py
@Create Time    : 2026-08-11 星期二 23:14:24
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 提供密码哈希与 JWT 访问令牌的安全基础能力
"""
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError
from pwdlib import PasswordHash

from app.core.config import Settings, get_settings

class InvalidAccessTokenError(ValueError):
    """表示访问令牌无法通过签名或声明校验。"""


_PASSWORD_HASH = PasswordHash.recommended()

def hash_password(password: str) -> str:
    """使用推荐的 Argon2 配置生成不可逆密码哈希。"""
    return _PASSWORD_HASH.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """校验明文密码是否匹配已保存的密码哈希。"""
    return _PASSWORD_HASH.verify(password, password_hash)


def create_access_token(
    subject: str,
    expires_delta: timedelta | None = None,
    *,
    settings: Settings | None = None,
) -> str:
    """使用应用 JWT 配置签发包含主题和过期时间的访问令牌。"""
    if not subject or subject.isspace():
        raise ValueError("访问令牌主题不能为空")

    config = settings or get_settings()
    lifetime = expires_delta
    if lifetime is None:
        lifetime = timedelta(minutes=config.JWT_ACCESS_TOKEN_EXPIRE_MINUTES)

    expires_at = datetime.now(timezone.utc) + lifetime
    claims = {"sub": subject, "exp": expires_at}
    return jwt.encode(
        claims,
        config.JWT_SECRET_KEY.get_secret_value(),
        algorithm=config.JWT_ALGORITHM,
    )


def decode_access_token(
    token: str,
    *,
    settings: Settings | None = None,
) -> str:
    """使用应用 JWT 配置验证访问令牌并返回非空字符串主题。"""
    config = settings or get_settings()
    try:
        claims: dict[str, Any] = jwt.decode(
            token,
            config.JWT_SECRET_KEY.get_secret_value(),
            algorithms=[config.JWT_ALGORITHM],
            options={"require": ["sub", "exp"]},
        )
    except InvalidTokenError as error:
        raise InvalidAccessTokenError("访问令牌无效") from error

    subject = claims["sub"]
    if not isinstance(subject, str) or not subject or subject.isspace():
        raise InvalidAccessTokenError("访问令牌主题无效")
    return subject


__all__ = [
    "InvalidAccessTokenError",
    "create_access_token",
    "decode_access_token",
    "hash_password",
    "verify_password",
]
