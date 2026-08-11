#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : health.py
@Create Time    : 2026-08-11 星期二 17:12:38
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 提供应用存活与 MongoDB 就绪健康检查端点
"""
from typing import Annotated

from fastapi import APIRouter, Depends, Request, Response, status

from app.schemas.health import (
    DependencyChecks,
    LivenessResponse,
    ReadinessResponse,
)
from app.services.health import HealthService


router = APIRouter(prefix="/health", tags=["health"])


def get_health_service(request: Request) -> HealthService:
    """从应用状态创建健康检查服务。"""
    try:
        database = request.app.state.mongodb
    except AttributeError as error:
        raise RuntimeError("MongoDB 应用状态尚未初始化") from error
    return HealthService(database)


@router.get(
    "/live",
    response_model=LivenessResponse,
    summary="检查应用进程是否存活",
)
async def check_liveness() -> LivenessResponse:
    """返回不依赖外部服务的进程存活状态。"""
    return LivenessResponse()


@router.get(
    "/ready",
    response_model=ReadinessResponse,
    responses={
        status.HTTP_503_SERVICE_UNAVAILABLE: {
            "model": ReadinessResponse,
            "description": "MongoDB 当前不可用",
        },
    },
    summary="检查应用及 MongoDB 是否就绪",
)
async def check_readiness(
    response: Response,
    health_service: Annotated[HealthService, Depends(get_health_service)],
) -> ReadinessResponse:
    """实时检查 MongoDB，并返回应用就绪状态。"""
    mongodb_ready = await health_service.is_mongodb_ready()
    if not mongodb_ready:
        response.status_code = status.HTTP_503_SERVICE_UNAVAILABLE
        return ReadinessResponse(
            status="not_ready",
            checks=DependencyChecks(mongodb="down"),
        )

    return ReadinessResponse(
        status="ready",
        checks=DependencyChecks(mongodb="up"),
    )


__all__ = ["router"]
