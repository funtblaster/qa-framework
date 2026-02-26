"""
utils/api_client.py
────────────────────
Reusable async HTTP client wrapper built on httpx.
Provides automatic auth headers, base URL injection, timeout defaults,
and structured logging for every request/response.

Usage:
    # In a fixture (see tests/conftest.py):
    client = ApiClient()

    # Sync usage
    response = client.get("/api/users")
    response = client.post("/api/users", json={"name": "Alice"})

    # Async usage
    response = await client.aget("/api/users")
"""

from __future__ import annotations

import json
import logging
from typing import Any

import httpx

from config.settings import settings

logger = logging.getLogger(__name__)


class ApiClient:
    """
    Thin wrapper around httpx that:
      - Prepends the configured API base URL
      - Injects auth headers from settings
      - Logs every request and response
      - Raises on 5xx by default (configurable)
    """

    def __init__(
        self,
        base_url: str | None = None,
        headers: dict[str, str] | None = None,
        timeout: int | None = None,
        raise_on_error: bool = False,
    ):
        self.base_url = (base_url or settings.api_base_url).rstrip("/")
        self.timeout = timeout or settings.request_timeout
        self.raise_on_error = raise_on_error

        default_headers = {
            "Content-Type": "application/json",
            "Accept": "application/json",
            **settings.auth_headers,
        }
        if headers:
            default_headers.update(headers)

        self._client = httpx.Client(
            base_url=self.base_url,
            headers=default_headers,
            timeout=self.timeout,
            verify=settings.verify_ssl,
        )
        self._async_client = httpx.AsyncClient(
            base_url=self.base_url,
            headers=default_headers,
            timeout=self.timeout,
            verify=settings.verify_ssl,
        )

    # ── Sync Methods ──────────────────────────────────────────────────────────

    def get(self, path: str, **kwargs) -> httpx.Response:
        return self._request("GET", path, **kwargs)

    def post(self, path: str, **kwargs) -> httpx.Response:
        return self._request("POST", path, **kwargs)

    def put(self, path: str, **kwargs) -> httpx.Response:
        return self._request("PUT", path, **kwargs)

    def patch(self, path: str, **kwargs) -> httpx.Response:
        return self._request("PATCH", path, **kwargs)

    def delete(self, path: str, **kwargs) -> httpx.Response:
        return self._request("DELETE", path, **kwargs)

    def _request(self, method: str, path: str, **kwargs) -> httpx.Response:
        url = path if path.startswith("http") else path
        logger.debug("→ %s %s%s  params=%s  body=%s",
                     method, self.base_url, url,
                     kwargs.get("params"), _truncate(kwargs.get("json") or kwargs.get("data")))

        response = self._client.request(method, url, **kwargs)

        logger.debug("← %s %s  (%.0fms)",
                     response.status_code, url, response.elapsed.total_seconds() * 1000)

        if self.raise_on_error:
            response.raise_for_status()

        return response

    # ── Async Methods ─────────────────────────────────────────────────────────

    async def aget(self, path: str, **kwargs) -> httpx.Response:
        return await self._arequest("GET", path, **kwargs)

    async def apost(self, path: str, **kwargs) -> httpx.Response:
        return await self._arequest("POST", path, **kwargs)

    async def aput(self, path: str, **kwargs) -> httpx.Response:
        return await self._arequest("PUT", path, **kwargs)

    async def apatch(self, path: str, **kwargs) -> httpx.Response:
        return await self._arequest("PATCH", path, **kwargs)

    async def adelete(self, path: str, **kwargs) -> httpx.Response:
        return await self._arequest("DELETE", path, **kwargs)

    async def _arequest(self, method: str, path: str, **kwargs) -> httpx.Response:
        logger.debug("→ %s %s%s", method, self.base_url, path)
        response = await self._async_client.request(method, path, **kwargs)
        logger.debug("← %s %s  (%.0fms)",
                     response.status_code, path, response.elapsed.total_seconds() * 1000)
        if self.raise_on_error:
            response.raise_for_status()
        return response

    # ── Auth helpers ──────────────────────────────────────────────────────────

    def set_auth_token(self, token: str) -> None:
        """Swap the bearer token mid-session (e.g. after login)."""
        self._client.headers["Authorization"] = f"Bearer {token}"
        self._async_client.headers["Authorization"] = f"Bearer {token}"

    def set_basic_auth(self, username: str, password: str) -> None:
        self._client.auth = (username, password)
        self._async_client.auth = (username, password)

    def clear_auth(self) -> None:
        self._client.headers.pop("Authorization", None)
        self._async_client.headers.pop("Authorization", None)

    # ── Context Manager ───────────────────────────────────────────────────────

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()

    def close(self) -> None:
        self._client.close()

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self._async_client.aclose()


def _truncate(obj: Any, max_len: int = 200) -> str:
    if obj is None:
        return ""
    s = json.dumps(obj) if isinstance(obj, dict) else str(obj)
    return s[:max_len] + "..." if len(s) > max_len else s
