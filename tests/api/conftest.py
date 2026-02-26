"""
tests/api/conftest.py
──────────────────────
API-specific fixtures: authenticated clients, shared test data.
"""

from __future__ import annotations

import pytest

from config.settings import settings
from utils.api_client import ApiClient


@pytest.fixture(scope="module")
def auth_api_client() -> ApiClient:
    """
    Module-scoped API client that has been authenticated.
    Performs login once per module and reuses the token.
    """
    client = ApiClient()

    if settings.api_token:
        # Token already configured — nothing to do
        return client

    if settings.test_username and settings.test_password:
        # Perform login to obtain a session token
        response = client.post(
            "/api/auth/login",
            json={"email": settings.test_username, "password": settings.test_password},
        )
        if response.status_code == 200:
            token = response.json().get("access_token") or response.json().get("token")
            if token:
                client.set_auth_token(token)

    return client
