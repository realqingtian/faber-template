#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : __init__.py
@Create Time    : 2026-08-11 星期二 17:08:01
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    :
"""
from beanie import Document

from app.models.user import User


# 所有 Beanie 文档模型都应在此注册，由数据库连接模块统一初始化。
DOCUMENT_MODELS: tuple[type[Document], ...] = (User,)


__all__ = ["DOCUMENT_MODELS", "User"]
