#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : __init__.py
@Create Time    : 2026-08-11 星期二 23:14:24
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 导出 JWT 身份认证 API 路由
"""
from app.api.auth.auth import router


__all__ = ["router"]
