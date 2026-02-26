"""
utils/assertions.py
────────────────────
Custom assertion helpers that produce clear, informative failure messages.
Import these instead of raw assert statements in test files.

Usage:
    from utils.assertions import assert_status, assert_schema, assert_contains

    assert_status(response, 200)
    assert_schema(response.json(), MyPydanticModel)
    assert_contains(response.json(), {"id": 1, "name": "Alice"})
"""

from __future__ import annotations

import json
from typing import Any, Type

import httpx
from pydantic import BaseModel, ValidationError


# ── HTTP Response Assertions ──────────────────────────────────────────────────

def assert_status(response: httpx.Response, expected: int) -> None:
    """Assert HTTP status code with a human-readable diff."""
    actual = response.status_code
    if actual != expected:
        body = _safe_body(response)
        raise AssertionError(
            f"Expected HTTP {expected}, got HTTP {actual}\n"
            f"URL: {response.url}\n"
            f"Body: {body}"
        )


def assert_status_in(response: httpx.Response, expected: list[int]) -> None:
    actual = response.status_code
    if actual not in expected:
        raise AssertionError(
            f"Expected HTTP status in {expected}, got {actual}\n"
            f"URL: {response.url}\n"
            f"Body: {_safe_body(response)}"
        )


def assert_ok(response: httpx.Response) -> None:
    """Assert 2xx status code."""
    if not (200 <= response.status_code < 300):
        raise AssertionError(
            f"Expected 2xx, got {response.status_code}\n"
            f"URL: {response.url}\n"
            f"Body: {_safe_body(response)}"
        )


def assert_header(response: httpx.Response, name: str, expected: str | None = None) -> None:
    """Assert that a response header exists, optionally checking its value."""
    if name.lower() not in response.headers:
        raise AssertionError(f"Expected header '{name}' not found in response\nHeaders: {dict(response.headers)}")
    if expected is not None:
        actual = response.headers[name.lower()]
        if actual != expected:
            raise AssertionError(f"Header '{name}': expected '{expected}', got '{actual}'")


def assert_response_time(response: httpx.Response, max_seconds: float) -> None:
    elapsed = response.elapsed.total_seconds()
    if elapsed > max_seconds:
        raise AssertionError(
            f"Response too slow: {elapsed:.2f}s > {max_seconds}s limit\n"
            f"URL: {response.url}"
        )


# ── JSON / Data Assertions ────────────────────────────────────────────────────

def assert_contains(actual: dict, expected: dict) -> None:
    """
    Assert that `actual` contains all key-value pairs in `expected`.
    Ignores extra keys in `actual`.
    """
    mismatches = {}
    missing = {}
    for key, expected_val in expected.items():
        if key not in actual:
            missing[key] = expected_val
        elif actual[key] != expected_val:
            mismatches[key] = {"expected": expected_val, "actual": actual[key]}

    errors = []
    if missing:
        errors.append(f"Missing keys: {json.dumps(missing, indent=2)}")
    if mismatches:
        errors.append(f"Value mismatches: {json.dumps(mismatches, indent=2, default=str)}")
    if errors:
        raise AssertionError("assert_contains failed:\n" + "\n".join(errors))


def assert_schema(data: dict | list, model: Type[BaseModel]) -> BaseModel | list[BaseModel]:
    """Validate JSON data against a Pydantic model, raising on schema violations."""
    try:
        if isinstance(data, list):
            return [model.model_validate(item) for item in data]
        return model.model_validate(data)
    except ValidationError as exc:
        raise AssertionError(
            f"Schema validation failed for {model.__name__}:\n{exc}"
        ) from exc


def assert_list_length(data: list, min_len: int = 0, max_len: int | None = None) -> None:
    length = len(data)
    if length < min_len:
        raise AssertionError(f"List too short: expected >= {min_len} items, got {length}")
    if max_len is not None and length > max_len:
        raise AssertionError(f"List too long: expected <= {max_len} items, got {length}")


def assert_sorted(data: list, key: str, reverse: bool = False) -> None:
    """Assert a list of dicts is sorted by a given key."""
    values = [item[key] for item in data]
    expected = sorted(values, reverse=reverse)
    if values != expected:
        raise AssertionError(
            f"List not sorted by '{key}' (reverse={reverse})\n"
            f"Got:      {values}\n"
            f"Expected: {expected}"
        )


def assert_unique(data: list, key: str) -> None:
    """Assert all values for a given key are unique across a list of dicts."""
    values = [item[key] for item in data]
    if len(values) != len(set(str(v) for v in values)):
        duplicates = [v for v in values if values.count(v) > 1]
        raise AssertionError(f"Duplicate values for '{key}': {duplicates}")


# ── UI / Text Assertions ──────────────────────────────────────────────────────

def assert_text_contains(actual: str, expected: str, case_sensitive: bool = True) -> None:
    a = actual if case_sensitive else actual.lower()
    e = expected if case_sensitive else expected.lower()
    if e not in a:
        raise AssertionError(
            f"Expected text to contain:\n  '{expected}'\nActual text:\n  '{actual[:300]}'"
        )


def assert_url_contains(actual_url: str, fragment: str) -> None:
    if fragment not in actual_url:
        raise AssertionError(
            f"Expected URL to contain '{fragment}'\nActual URL: '{actual_url}'"
        )


# ── Internal Helpers ──────────────────────────────────────────────────────────

def _safe_body(response: httpx.Response, max_len: int = 500) -> str:
    try:
        body = json.dumps(response.json(), indent=2)
    except Exception:
        body = response.text
    return body[:max_len] + ("..." if len(body) > max_len else "")
