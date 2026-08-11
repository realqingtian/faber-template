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


class InvalidAccessTokenError(ValueError):
    """表示访问令牌无法通过签名或声明校验。"""


_PASSWORD_HASH = PasswordHash.recommended()
# 用于测试的密码哈希
DUMMY_PASSWORD_HASH = _PASSWORD_HASH.hash("UbMifzHP7thhc7Gjbjni")


def hash_password(password: str) -> str:
    """使用推荐的 Argon2 配置生成不可逆密码哈希。"""
    return _PASSWORD_HASH.hash(password)


def verify_password(password: str, password_hash: str) -> bool:
    """校验明文密码是否匹配已保存的密码哈希。"""
    return _PASSWORD_HASH.verify(password, password_hash)


def create_access_token(
    subject: str,
    secret_key: str,
    algorithm: str,
    expires_delta: timedelta,
) -> str:
    """创建包含字符串主题和过期时间的 JWT 访问令牌。"""
    expires_at = datetime.now(timezone.utc) + expires_delta
    claims = {"sub": subject, "exp": expires_at}
    return jwt.encode(claims, secret_key, algorithm=algorithm)


def decode_access_token(
    token: str,
    secret_key: str,
    algorithm: str,
) -> str:
    """验证 JWT 并返回非空字符串主题。"""
    try:
        claims: dict[str, Any] = jwt.decode(
            token,
            secret_key,
            algorithms=[algorithm],
            options={"require": ["sub", "exp"]},
        )
        subject = claims.get("sub")
        if not isinstance(subject, str) or not subject:
            raise InvalidAccessTokenError("访问令牌主题无效")
        return subject
    except InvalidTokenError as error:
        raise InvalidAccessTokenError("访问令牌无效") from error


__all__ = [
    "DUMMY_PASSWORD_HASH",
    "InvalidAccessTokenError",
    "create_access_token",
    "decode_access_token",
    "hash_password",
    "verify_password",
]
