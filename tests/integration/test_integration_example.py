"""
tests/integration/test_integration_example.py
──────────────────────────────────────────────
End-to-end integration tests that exercise multiple layers together.
These typically take longer and run in the nightly suite.

Examples here demonstrate:
  - Webhook simulation with pytest-httpserver
  - Async polling for eventual consistency
  - UI → API state verification

Run with:
    pytest tests/integration/ -v
    pytest -m integration -v
"""

from __future__ import annotations

import json

import pytest

from utils import ApiClient, assert_status, poll_until
from utils.data_factory import DataFactory


# ─────────────────────────────────────────────────────────────────────────────
# Webhook / Async Flow Tests
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
@pytest.mark.p1
@pytest.mark.slow
class TestWebhookSimulation:
    """
    Simulate inbound webhooks using pytest-httpserver.
    Demonstrates how to test async flows and callback handling.
    """

    def test_webhook_endpoint_accepts_post(self, api_client: ApiClient, httpserver):
        """
        Simulate a third-party webhook:
        1. Register a local mock server to receive callbacks
        2. Trigger an action in the app that should fire a webhook
        3. Assert the mock server received the expected payload
        """
        received = []

        # Set up a local mock server that captures the webhook
        httpserver.expect_request("/webhook", method="POST").respond_with_handler(
            lambda req: (received.append(json.loads(req.data)), None)[1]
            or __import__("werkzeug").wrappers.Response("OK", status=200)
        )

        # This is a template — adapt to your app's webhook trigger mechanism.
        # Example: tell your app to send a webhook to our mock server.
        # resp = api_client.post("/api/webhooks/test", json={
        #     "callback_url": httpserver.url_for("/webhook"),
        #     "event": "payment.completed",
        # })
        # assert_status(resp, 200)

        # Then poll until the webhook arrives
        # try:
        #     poll_until(lambda: len(received) > 0, condition=bool, timeout=10)
        # except TimeoutError:
        #     pytest.fail("Webhook was not received within 10 seconds")
        #
        # payload = received[0]
        # assert payload["event"] == "payment.completed"

        pytest.skip(
            "Configure the webhook trigger in your application. "
            "See comments in this test for the pattern."
        )

    def test_idempotent_webhook_delivery(self, api_client: ApiClient):
        """
        Sending the same webhook twice should not cause duplicate side effects.
        The application should handle idempotency keys or deduplication.
        """
        # Template — implement for your specific webhook endpoint
        pytest.skip("Implement idempotency test for your webhook endpoint")


# ─────────────────────────────────────────────────────────────────────────────
# UI + API State Consistency
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
@pytest.mark.p1
class TestUIAPIConsistency:
    """
    Verify that actions taken via the UI are reflected correctly in the API,
    and vice versa. These tests exercise the full stack.
    """

    def test_data_created_via_api_appears_in_ui(self, api_client: ApiClient, page):
        """
        1. Create a resource via API
        2. Navigate to the UI page that lists it
        3. Assert it appears in the UI
        """
        pytest.skip(
            "Implement this test by:\n"
            "  1. POST to your API to create a resource\n"
            "  2. Navigate to the corresponding UI page\n"
            "  3. Assert the resource is visible"
        )

    def test_deletion_via_ui_removes_from_api(self, api_client: ApiClient, authenticated_page):
        """
        1. Create a resource via API
        2. Delete it via the UI
        3. Confirm the API returns 404 for that resource
        """
        pytest.skip(
            "Implement this test by:\n"
            "  1. Create a resource via API\n"
            "  2. Navigate to the UI and delete it\n"
            "  3. Assert the API returns 404"
        )


# ─────────────────────────────────────────────────────────────────────────────
# Async Polling Pattern
# ─────────────────────────────────────────────────────────────────────────────

@pytest.mark.integration
@pytest.mark.p2
@pytest.mark.slow
class TestAsyncJobPolling:
    """
    Template for testing long-running async jobs.
    Pattern: trigger job → poll until complete → assert final state.
    """

    def test_async_job_completes_successfully(self, api_client: ApiClient):
        """
        Trigger an async job and poll until it reaches a terminal state.
        """
        # Step 1: Trigger the job
        # resp = api_client.post("/api/jobs", json={"type": "export", ...})
        # assert_status(resp, 202)
        # job_id = resp.json()["id"]

        # Step 2: Poll until complete
        # try:
        #     final = poll_until(
        #         fn=lambda: api_client.get(f"/api/jobs/{job_id}").json(),
        #         condition=lambda r: r["status"] in ("complete", "failed"),
        #         timeout=60,
        #         interval=2,
        #         message=f"Job {job_id} did not complete",
        #     )
        # except TimeoutError as exc:
        #     pytest.fail(str(exc))

        # Step 3: Assert success
        # assert final["status"] == "complete", f"Job failed: {final}"

        pytest.skip(
            "Configure the async job endpoint for your application. "
            "See comments in this test for the pattern."
        )
