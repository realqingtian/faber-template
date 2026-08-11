#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : auth.py
@Create Time    : 2026-08-11 星期二 23:14:24
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 定义身份认证端点的公开请求与响应模型
"""
from typing import Literal

from pydantic import BaseModel, ConfigDict


class TokenResponse(BaseModel):
    """OAuth2 Bearer 访问令牌响应。"""

    access_token: str
    token_type: Literal["bearer"] = "bearer"


class UserResponse(BaseModel):
    """对外公开的当前用户资料。"""

    model_config = ConfigDict(from_attributes=True)

    username: str
    email: str | None = None
    full_name: str | None = None
    disabled: bool = False


__all__ = ["TokenResponse", "UserResponse"]
