#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : router.py
@Create Time    : 2026-08-12 星期三 22:52:06
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 
"""
from fastapi import APIRouter


router = APIRouter(tags=["Health Check"])


@router.get("/health", summary="Health Check")
def health_check():
    return {"status": "healthy"}
