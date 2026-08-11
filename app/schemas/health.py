#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : health.py
@Create Time    : 2026-08-11 星期二 20:16:02
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 定义健康检查端点的公开响应模型
"""
from typing import Literal

from pydantic import BaseModel


class DependencyChecks(BaseModel):
    """外部依赖的实时健康状态。"""

    mongodb: Literal["up", "down"]


class LivenessResponse(BaseModel):
    """进程存活检查响应。"""

    status: Literal["ok"] = "ok"


class ReadinessResponse(BaseModel):
    """应用就绪检查响应。"""

    status: Literal["ready", "not_ready"]
    checks: DependencyChecks


__all__ = ["DependencyChecks", "LivenessResponse", "ReadinessResponse"]
