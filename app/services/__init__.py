#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : __init__.py
@Create Time    : 2026-08-11 星期二 17:07:19
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 导出应用业务服务
"""
from app.services.auth import AuthService
from app.services.health import HealthService


__all__ = ["AuthService", "HealthService"]
