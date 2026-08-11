#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : __init__.py
@Create Time    : 2026-08-11 星期二 17:07:00
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 导出应用数据访问仓储
"""
from app.repositories.users import UserRepository


__all__ = ["UserRepository"]
