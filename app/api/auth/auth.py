#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : auth.py
@Create Time    : 2026-08-11 星期二 23:14:24
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 提供 OAuth2 密码登录与当前用户端点
"""
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

from app.core.config import get_settings
from app.core.security import InvalidAccessTokenError
from app.models import User
from app.repositories import UserRepository
from app.schemas import TokenResponse, UserResponse
from app.services import AuthService


router = APIRouter(prefix="/auth", tags=["auth"])
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="auth/token")


def get_auth_service() -> AuthService:
    """使用应用配置和用户仓储创建认证服务。"""
    return AuthService(UserRepository(), get_settings())


def _credentials_exception() -> HTTPException:
    """构造不泄露认证失败原因的标准 Bearer 错误。"""
    return HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )


async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> User:
    """从 Bearer 令牌解析当前用户。"""
    try:
        user = await auth_service.resolve_user(token)
    except InvalidAccessTokenError as error:
        raise _credentials_exception() from error
    if user is None:
        raise _credentials_exception()
    return user


async def get_current_active_user(
    current_user: Annotated[User, Depends(get_current_user)],
) -> User:
    """拒绝已停用用户并返回当前可用用户。"""
    if current_user.disabled:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Inactive user",
        )
    return current_user


@router.post(
    "/token",
    response_model=TokenResponse,
    summary="使用用户名和密码获取访问令牌",
)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    auth_service: Annotated[AuthService, Depends(get_auth_service)],
) -> TokenResponse:
    """验证 OAuth2 密码表单并签发 Bearer 访问令牌。"""
    user = await auth_service.authenticate(form_data.username, form_data.password)
    if user is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return TokenResponse(access_token=auth_service.issue_access_token(user))


@router.get(
    "/me",
    response_model=UserResponse,
    summary="获取当前已认证用户",
)
async def read_current_user(
    current_user: Annotated[User, Depends(get_current_active_user)],
) -> UserResponse:
    """返回当前有效用户的公开资料。"""
    return UserResponse.model_validate(current_user)


__all__ = [
    "get_auth_service",
    "get_current_active_user",
    "get_current_user",
    "oauth2_scheme",
    "router",
]
