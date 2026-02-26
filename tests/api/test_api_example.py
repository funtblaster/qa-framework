"""
tests/api/test_api_example.py
──────────────────────────────
Example API tests demonstrating framework usage.
Replace endpoints and assertions with those matching your application.

Run with:
    pytest tests/api/ -v
    pytest -m api -v
"""

from __future__ import annotations

import pytest

from utils import ApiClient, assert_status, assert_ok, assert_contains, assert_response_time
from utils.data_factory import DataFactory


# ─────────────────────────────────────────────────────────────────────────────
# Health / Status Endpoint
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.smoke
@pytest.mark.api
@pytest.mark.p0
class TestHealthEndpoint:
    """
    The application should expose a health/status endpoint.
    Common paths: /health, /api/health, /status, /ping

    Adjust the path(s) to match your application.
    """

    HEALTH_PATHS = ["/health", "/api/health", "/status", "/ping", "/api/ping"]

    def test_health_endpoint_returns_200(self, api_client: ApiClient):
        """At least one health endpoint should return 200."""
        for path in self.HEALTH_PATHS:
            resp = api_client.get(path)
            if resp.status_code == 200:
                return  # Pass as soon as we find a working one
        pytest.skip(
            f"No health endpoint found at: {self.HEALTH_PATHS}. "
            "Add the correct path for your application."
        )

    def test_health_response_is_fast(self, api_client: ApiClient):
        """Health check should respond within 1 second."""
        for path in self.HEALTH_PATHS:
            resp = api_client.get(path)
            if resp.status_code == 200:
                assert_response_time(resp, max_seconds=1.0)
                return


# ─────────────────────────────────────────────────────────────────────────────
# Generic CRUD Patterns
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.api
@pytest.mark.p1
class TestGenericListEndpoint:
    """
    Generic tests for a list/collection API endpoint.
    Configure ENDPOINT to target your application's resource.
    """

    # ── Configure these for your application ────────────────────────────────
    ENDPOINT = "/api/items"   # e.g. /api/users, /api/products, /api/posts
    # ─────────────────────────────────────────────────────────────────────────

    def test_list_returns_200(self, api_client: ApiClient):
        resp = api_client.get(self.ENDPOINT)
        assert resp.status_code in (200, 404), (
            f"Expected 200 or 404 for {self.ENDPOINT}, got {resp.status_code}. "
            "Update ENDPOINT in this test class."
        )

    def test_list_response_is_json(self, api_client: ApiClient):
        resp = api_client.get(self.ENDPOINT)
        if resp.status_code != 200:
            pytest.skip(f"Endpoint {self.ENDPOINT} returned {resp.status_code}")
        # Should parse as JSON without raising
        data = resp.json()
        assert data is not None

    def test_list_returns_array_or_paginated_object(self, api_client: ApiClient):
        """Response should be a list OR an object containing a list."""
        resp = api_client.get(self.ENDPOINT)
        if resp.status_code != 200:
            pytest.skip(f"Endpoint {self.ENDPOINT} returned {resp.status_code}")
        data = resp.json()
        assert isinstance(data, (list, dict)), (
            f"Expected list or dict, got {type(data).__name__}"
        )


@pytest.mark.api
@pytest.mark.p1
class TestGenericCRUD:
    """
    Template for CRUD endpoint tests.
    Configure ENDPOINT and NEW_ITEM_BODY to match your API.
    """

    ENDPOINT = "/api/items"
    NEW_ITEM_BODY: dict = {}  # Override with the body your API expects

    def test_create_returns_201_or_200(self, api_client: ApiClient):
        if not self.NEW_ITEM_BODY:
            pytest.skip("NEW_ITEM_BODY not configured — set it in a subclass")
        resp = api_client.post(self.ENDPOINT, json=self.NEW_ITEM_BODY)
        assert resp.status_code in (200, 201), (
            f"Expected 200 or 201 for POST {self.ENDPOINT}, got {resp.status_code}\n"
            f"Body: {resp.text[:200]}"
        )

    def test_create_returns_an_id(self, api_client: ApiClient):
        if not self.NEW_ITEM_BODY:
            pytest.skip("NEW_ITEM_BODY not configured")
        resp = api_client.post(self.ENDPOINT, json=self.NEW_ITEM_BODY)
        if resp.status_code not in (200, 201):
            pytest.skip(f"Create returned {resp.status_code}")
        data = resp.json()
        assert "id" in data or "_id" in data, (
            f"Response should contain an id field. Got keys: {list(data.keys())}"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Auth / Security Boundary Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.api
@pytest.mark.p0
class TestAuthBoundaries:
    """
    Ensure protected endpoints reject unauthenticated requests.
    These tests use a client with NO auth headers.
    """

    PROTECTED_ENDPOINTS = [
        "/api/users/me",
        "/api/profile",
        "/api/account",
        "/api/dashboard",
    ]

    def test_protected_endpoints_reject_unauthenticated(self):
        """Endpoints requiring auth should return 401 or 403 without credentials."""
        unauthenticated_client = ApiClient()
        unauthenticated_client.clear_auth()

        tested = 0
        for path in self.PROTECTED_ENDPOINTS:
            resp = unauthenticated_client.get(path)
            if resp.status_code in (404, 405):
                continue  # endpoint doesn't exist — skip
            tested += 1
            assert resp.status_code in (401, 403), (
                f"Expected 401/403 for unauthenticated GET {path}, got {resp.status_code}"
            )

        if tested == 0:
            pytest.skip(
                "None of the configured protected endpoints exist. "
                "Update PROTECTED_ENDPOINTS in TestAuthBoundaries."
            )

    def test_invalid_token_is_rejected(self):
        """A request with a forged/expired token should be rejected."""
        client = ApiClient()
        client.set_auth_token("this.is.definitely.not.a.valid.token")

        for path in self.PROTECTED_ENDPOINTS:
            resp = client.get(path)
            if resp.status_code == 404:
                continue
            assert resp.status_code in (401, 403), (
                f"Expected 401/403 with invalid token for GET {path}, got {resp.status_code}"
            )
            return  # Only need one passing example

        pytest.skip("No protected endpoints to test against")


# ─────────────────────────────────────────────────────────────────────────────
# Error Handling Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.api
@pytest.mark.p1
class TestErrorHandling:
    """API should return structured errors, not stack traces."""

    def test_404_returns_json(self, api_client: ApiClient):
        """A 404 response should return JSON, not HTML."""
        resp = api_client.get("/api/this-endpoint-does-not-exist-xyz-987")
        if resp.status_code not in (404, 400):
            pytest.skip("App does not return 404 for unknown API routes")
        content_type = resp.headers.get("content-type", "")
        assert "application/json" in content_type or resp.json() is not None, (
            f"Expected JSON error response, got content-type: {content_type}"
        )

    def test_malformed_json_body_returns_400(self, api_client: ApiClient):
        """Sending malformed JSON should return 400, not 500."""
        resp = api_client._client.post(
            "/api/items",
            content=b"{invalid json}",
            headers={"Content-Type": "application/json"},
        )
        assert resp.status_code in (400, 422, 404), (
            f"Expected 400/422 for malformed JSON, got {resp.status_code}"
        )
