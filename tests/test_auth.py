#!/usr/bin/env python3
"""
@Project        : faber-template
@Author         : 晴天
@Email          : realqingtian@outlook.com
@File           : test_auth.py
@Create Time    : 2026-08-11 星期二 23:14:24
@Copyright      : (c) 2026 晴天 All Rights Reserved
@Description    : JWT 安全能力、认证服务和认证端点的回归测试
"""
import os
import unittest
from datetime import timedelta
from unittest.mock import AsyncMock, MagicMock, patch

import jwt
from fastapi.testclient import TestClient

from app.api.auth.auth import get_auth_service
from app.app_factory import create_app
from app.core.config import get_settings
from app.core.security import (
    DUMMY_PASSWORD_HASH,
    InvalidAccessTokenError,
    create_access_token,
    decode_access_token,
    hash_password,
    verify_password,
)
from app.database import MongoDatabase
from app.models import User
from app.repositories import UserRepository
from app.services import AuthService
from tests.settings_factory import TEST_JWT_SECRET_KEY, build_isolated_settings


class SecurityTests(unittest.TestCase):
    def test_password_is_hashed_with_argon2_and_can_be_verified(self) -> None:
        password_hash = hash_password("correct horse battery staple")

        self.assertTrue(password_hash.startswith("$argon2"))
        self.assertTrue(
            verify_password("correct horse battery staple", password_hash)
        )
        self.assertFalse(verify_password("wrong password", password_hash))

    def test_access_token_round_trip_returns_subject(self) -> None:
        token = create_access_token(
            subject="johndoe",
            secret_key=TEST_JWT_SECRET_KEY,
            algorithm="HS256",
            expires_delta=timedelta(minutes=5),
        )

        self.assertEqual(
            decode_access_token(token, TEST_JWT_SECRET_KEY, "HS256"),
            "johndoe",
        )

    def test_expired_access_token_is_rejected(self) -> None:
        token = create_access_token(
            subject="johndoe",
            secret_key=TEST_JWT_SECRET_KEY,
            algorithm="HS256",
            expires_delta=timedelta(seconds=-1),
        )

        with self.assertRaises(InvalidAccessTokenError):
            decode_access_token(token, TEST_JWT_SECRET_KEY, "HS256")

    def test_token_without_required_subject_is_rejected(self) -> None:
        token = jwt.encode(
            {"exp": 4102444800},
            TEST_JWT_SECRET_KEY,
            algorithm="HS256",
        )

        with self.assertRaises(InvalidAccessTokenError):
            decode_access_token(token, TEST_JWT_SECRET_KEY, "HS256")

    def test_token_signed_with_another_key_is_rejected(self) -> None:
        token = create_access_token(
            subject="johndoe",
            secret_key="another-test-only-secret-key-32-chars",
            algorithm="HS256",
            expires_delta=timedelta(minutes=5),
        )

        with self.assertRaises(InvalidAccessTokenError):
            decode_access_token(token, TEST_JWT_SECRET_KEY, "HS256")


class AuthServiceTests(unittest.IsolatedAsyncioTestCase):
    def setUp(self) -> None:
        self.repository = MagicMock(spec=UserRepository)
        self.repository.get_by_username = AsyncMock()
        self.settings = build_isolated_settings()
        self.service = AuthService(self.repository, self.settings)
        self.user = User.model_construct(
            username="johndoe",
            email="john@example.com",
            full_name="John Doe",
            hashed_password="stored-password-hash",
        )

    async def test_authenticate_returns_user_for_matching_password(self) -> None:
        self.repository.get_by_username.return_value = self.user

        with patch("app.services.auth.verify_password", return_value=True):
            result = await self.service.authenticate("johndoe", "secret")

        self.assertIs(result, self.user)

    async def test_authenticate_rejects_wrong_password(self) -> None:
        self.repository.get_by_username.return_value = self.user

        with patch("app.services.auth.verify_password", return_value=False):
            result = await self.service.authenticate("johndoe", "wrong")

        self.assertIsNone(result)

    async def test_missing_user_still_verifies_dummy_hash(self) -> None:
        self.repository.get_by_username.return_value = None

        with patch(
            "app.services.auth.verify_password",
            return_value=False,
        ) as verify:
            result = await self.service.authenticate("missing", "secret")

        self.assertIsNone(result)
        verify.assert_called_once_with("secret", DUMMY_PASSWORD_HASH)

    async def test_resolve_user_uses_token_subject_for_lookup(self) -> None:
        self.repository.get_by_username.return_value = self.user
        token = self.service.issue_access_token(self.user)

        result = await self.service.resolve_user(token)

        self.assertIs(result, self.user)
        self.repository.get_by_username.assert_awaited_once_with("johndoe")

    async def test_repository_failure_is_not_silently_swallowed(self) -> None:
        self.repository.get_by_username.side_effect = RuntimeError("database down")

        with self.assertRaisesRegex(RuntimeError, "database down"):
            await self.service.authenticate("johndoe", "secret")


class AuthApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.jwt_environment = patch.dict(
            os.environ,
            {"JWT_SECRET_KEY": TEST_JWT_SECRET_KEY},
        )
        self.jwt_environment.start()
        get_settings.cache_clear()

        self.setup_logging_patcher = patch("app.app_factory.setup_logging")
        self.setup_logging_patcher.start()
        self.database = MagicMock(spec=MongoDatabase)
        self.database.connect = AsyncMock()
        self.database.disconnect = AsyncMock()
        self.auth_service = MagicMock(spec=AuthService)
        self.auth_service.authenticate = AsyncMock()
        self.auth_service.resolve_user = AsyncMock()

        self.app = create_app()
        self.app.dependency_overrides[get_auth_service] = lambda: self.auth_service
        self.mongodb_patcher = patch("app.core.lifespan.mongodb", self.database)
        self.mongodb_patcher.start()
        self.client_context = TestClient(self.app)
        self.client = self.client_context.__enter__()

    def tearDown(self) -> None:
        self.client_context.__exit__(None, None, None)
        self.app.dependency_overrides.clear()
        self.mongodb_patcher.stop()
        self.setup_logging_patcher.stop()
        self.jwt_environment.stop()
        get_settings.cache_clear()

    @staticmethod
    def _user(disabled: bool = False) -> User:
        """构造不依赖真实数据库的认证用户。"""
        return User.model_construct(
            username="johndoe",
            email="john@example.com",
            full_name="John Doe",
            hashed_password="must-not-be-returned",
            disabled=disabled,
        )

    def test_token_endpoint_returns_bearer_token(self) -> None:
        user = self._user()
        self.auth_service.authenticate.return_value = user
        self.auth_service.issue_access_token.return_value = "signed-token"

        response = self.client.post(
            "/auth/token",
            data={"username": "johndoe", "password": "secret"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {"access_token": "signed-token", "token_type": "bearer"},
        )
        self.auth_service.authenticate.assert_awaited_once_with(
            "johndoe",
            "secret",
        )

    def test_token_endpoint_rejects_invalid_credentials_uniformly(self) -> None:
        self.auth_service.authenticate.return_value = None

        response = self.client.post(
            "/auth/token",
            data={"username": "missing", "password": "wrong"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(
            response.json(),
            {"detail": "Incorrect username or password"},
        )
        self.assertEqual(response.headers["www-authenticate"], "Bearer")

    def test_token_endpoint_validates_oauth2_form(self) -> None:
        response = self.client.post(
            "/auth/token",
            data={"username": "johndoe"},
        )

        self.assertEqual(response.status_code, 422)
        self.auth_service.authenticate.assert_not_awaited()

    def test_me_returns_only_public_active_user_fields(self) -> None:
        self.auth_service.resolve_user.return_value = self._user()

        response = self.client.get(
            "/auth/me",
            headers={"Authorization": "Bearer valid-token"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "username": "johndoe",
                "email": "john@example.com",
                "full_name": "John Doe",
                "disabled": False,
            },
        )
        self.assertNotIn("hashed_password", response.text)

    def test_me_rejects_invalid_token_with_bearer_challenge(self) -> None:
        self.auth_service.resolve_user.side_effect = InvalidAccessTokenError()

        response = self.client.get(
            "/auth/me",
            headers={"Authorization": "Bearer invalid-token"},
        )

        self.assertEqual(response.status_code, 401)
        self.assertEqual(response.headers["www-authenticate"], "Bearer")
        self.assertEqual(
            response.json(),
            {"detail": "Could not validate credentials"},
        )

    def test_me_rejects_disabled_user(self) -> None:
        self.auth_service.resolve_user.return_value = self._user(disabled=True)

        response = self.client.get(
            "/auth/me",
            headers={"Authorization": "Bearer valid-token"},
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.json(), {"detail": "Inactive user"})


if __name__ == "__main__":
    unittest.main()
