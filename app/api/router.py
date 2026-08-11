#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : router.py
@Create Time    : 2026-08-11 星期二 17:12:28
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 汇总并导出应用的顶层 API 路由
"""
from fastapi import APIRouter

from app.api.auth import router as auth_router
from app.api.health import router as health_router


api_router = APIRouter()
api_router.include_router(auth_router)
api_router.include_router(health_router)


__all__ = ["api_router"]
