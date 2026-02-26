"""
utils/retry.py
───────────────
Retry and wait utilities for dealing with async flows, eventual consistency,
and flaky external services.

Usage:
    from utils.retry import retry, wait_until, poll_until

    # Decorator
    @retry(times=3, delay=1.0, exceptions=(httpx.TimeoutException,))
    def fragile_api_call():
        ...

    # Wait for a condition
    result = wait_until(lambda: api.get_job_status() == "complete", timeout=30)

    # Poll an API endpoint
    data = poll_until(
        fn=lambda: client.get("/jobs/123").json(),
        condition=lambda r: r["status"] == "complete",
        timeout=60
    )
"""

from __future__ import annotations

import asyncio
import functools
import logging
import time
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def retry(
    times: int = 3,
    delay: float = 1.0,
    backoff: float = 1.0,
    exceptions: tuple = (Exception,),
    on_retry: Callable[[Exception, int], None] | None = None,
):
    """
    Decorator that retries a function on specified exceptions.

    Args:
        times:      Maximum number of attempts (default 3)
        delay:      Initial delay between retries in seconds
        backoff:    Multiplier applied to delay after each retry (1.0 = constant)
        exceptions: Tuple of exception types to catch
        on_retry:   Optional callback(exc, attempt_number) called before each retry
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            current_delay = delay
            last_exc: Exception | None = None
            for attempt in range(1, times + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as exc:
                    last_exc = exc
                    if attempt == times:
                        break
                    logger.warning(
                        "Retry %d/%d for %s: %s. Waiting %.1fs…",
                        attempt, times, func.__name__, exc, current_delay
                    )
                    if on_retry:
                        on_retry(exc, attempt)
                    time.sleep(current_delay)
                    current_delay *= backoff
            raise last_exc  # type: ignore[misc]
        return wrapper

    return decorator


def wait_until(
    condition: Callable[[], bool],
    timeout: float = 30.0,
    interval: float = 0.5,
    message: str = "Condition not met",
) -> None:
    """
    Poll `condition()` until it returns True or `timeout` seconds elapse.

    Raises:
        TimeoutError: if condition is not met within `timeout` seconds
    """
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if condition():
            return
        time.sleep(interval)
    raise TimeoutError(f"{message} after {timeout}s")


def poll_until(
    fn: Callable[[], T],
    condition: Callable[[T], bool],
    timeout: float = 30.0,
    interval: float = 1.0,
    message: str = "Polling condition not met",
) -> T:
    """
    Repeatedly call `fn()` until `condition(result)` is True.

    Returns the final result that satisfied the condition.

    Example:
        data = poll_until(
            fn=lambda: client.get("/jobs/123").json(),
            condition=lambda r: r["status"] == "complete",
            timeout=60,
        )
    """
    deadline = time.monotonic() + timeout
    last_result: T | None = None
    while time.monotonic() < deadline:
        last_result = fn()
        if condition(last_result):
            return last_result  # type: ignore[return-value]
        time.sleep(interval)
    raise TimeoutError(f"{message} after {timeout}s. Last result: {last_result}")


async def async_wait_until(
    condition: Callable[[], Any],
    timeout: float = 30.0,
    interval: float = 0.5,
    message: str = "Async condition not met",
) -> None:
    """Async variant of wait_until."""
    deadline = asyncio.get_event_loop().time() + timeout
    while asyncio.get_event_loop().time() < deadline:
        result = condition()
        if asyncio.iscoroutine(result):
            result = await result
        if result:
            return
        await asyncio.sleep(interval)
    raise TimeoutError(f"{message} after {timeout}s")


async def async_poll_until(
    fn: Callable[[], Any],
    condition: Callable[[Any], bool],
    timeout: float = 30.0,
    interval: float = 1.0,
    message: str = "Async polling condition not met",
) -> Any:
    """Async variant of poll_until."""
    deadline = asyncio.get_event_loop().time() + timeout
    last_result = None
    while asyncio.get_event_loop().time() < deadline:
        result = fn()
        if asyncio.iscoroutine(result):
            result = await result
        last_result = result
        if condition(result):
            return result
        await asyncio.sleep(interval)
    raise TimeoutError(f"{message} after {timeout}s. Last result: {last_result}")
