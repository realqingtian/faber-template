#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : logging.py
@Create Time    : 2026-08-12 星期三 23:35:59
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : 
"""
import time
import uuid

from fastapi import Request
from starlette.types import ASGIApp, Receive, Scope, Send
from loguru import logger


class LoggingMiddleware:
    """
    ASGI 日志中间件
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        request = Request(scope, receive=receive)
        request_id = request.headers.get("X-Request-ID") or str(uuid.uuid4())

        # 把 request_id 挂到 request.state，方便后续使用
        request.state.request_id = request_id

        start_time = time.time()

        with logger.contextualize(request_id=request_id):
            logger.info(
                f"→ {request.method} {request.url.path} "
                f"| client={request.client if request.client else 'unknown'}"
            )

            # 用于捕获最终状态码
            status_code = 500

            async def send_wrapper(message):
                nonlocal status_code
                if message["type"] == "http.response.start":
                    status_code = message["status"]
                    # 把 request_id 写回响应头
                    headers = list(message.get("headers", []))
                    headers.append((b"x-request-id", request_id.encode()))
                    message = {**message, "headers": headers}
                await send(message)

            try:
                await self.app(scope, receive, send_wrapper)
            except Exception:
                process_time = (time.time() - start_time) * 1000
                logger.exception(
                    f"← {request.method} {request.url.path} "
                    f"| status=500 | time={process_time:.2f}ms"
                )
                raise
            else:
                process_time = (time.time() - start_time) * 1000
                log_func = logger.info if status_code < 400 else logger.warning
                if status_code >= 500:
                    log_func = logger.error

                log_func(
                    f"← {request.method} {request.url.path} "
                    f"| status={status_code} | time={process_time:.2f}ms"
                )