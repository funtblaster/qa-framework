"""
utils/data_factory.py
──────────────────────
Test data generation using Faker.
Provides reusable factories for common entities.
Extend this module with domain-specific factories for your application.

Usage:
    from utils.data_factory import DataFactory

    user = DataFactory.user()
    # {'email': 'alice.smith@example.net', 'username': 'alice_smith_42', ...}

    unique_email = DataFactory.unique_email()
"""

from __future__ import annotations

import random
import string
import uuid
from datetime import datetime, timedelta
from typing import Any

from faker import Faker

fake = Faker()
Faker.seed(0)  # Deterministic seed — override per-test if needed


class DataFactory:
    """
    Static factory methods for generating test data.
    Each method returns a plain dict ready to use as JSON body or fixture.
    """

    # ── Users / Auth ──────────────────────────────────────────────────────────

    @staticmethod
    def user(
        email: str | None = None,
        username: str | None = None,
        password: str | None = None,
        **overrides,
    ) -> dict[str, Any]:
        first = fake.first_name()
        last = fake.last_name()
        return {
            "first_name": first,
            "last_name": last,
            "username": username or f"{first.lower()}_{last.lower()}_{random.randint(10, 99)}",
            "email": email or fake.unique.email(),
            "password": password or _strong_password(),
            "phone": fake.phone_number(),
            **overrides,
        }

    @staticmethod
    def unique_email(domain: str = "example.com") -> str:
        return f"qa_{uuid.uuid4().hex[:8]}@{domain}"

    @staticmethod
    def address() -> dict[str, Any]:
        return {
            "street": fake.street_address(),
            "city": fake.city(),
            "state": fake.state(),
            "postal_code": fake.postcode(),
            "country": fake.country_code(),
        }

    # ── Generic Primitives ────────────────────────────────────────────────────

    @staticmethod
    def uuid() -> str:
        return str(uuid.uuid4())

    @staticmethod
    def random_string(length: int = 12) -> str:
        return "".join(random.choices(string.ascii_letters, k=length))

    @staticmethod
    def random_int(min_val: int = 1, max_val: int = 1000) -> int:
        return random.randint(min_val, max_val)

    @staticmethod
    def future_date(days: int = 30) -> str:
        """ISO 8601 date string for a date in the future."""
        return (datetime.utcnow() + timedelta(days=days)).strftime("%Y-%m-%d")

    @staticmethod
    def past_date(days: int = 30) -> str:
        return (datetime.utcnow() - timedelta(days=days)).strftime("%Y-%m-%d")

    @staticmethod
    def timestamp_now() -> str:
        return datetime.utcnow().isoformat() + "Z"

    # ── HTTP / API Helpers ────────────────────────────────────────────────────

    @staticmethod
    def pagination_params(page: int = 1, page_size: int = 20) -> dict[str, int]:
        return {"page": page, "page_size": page_size}

    @staticmethod
    def search_params(query: str | None = None) -> dict[str, str]:
        return {"q": query or fake.word()}

    # ── Seed helpers ──────────────────────────────────────────────────────────

    @staticmethod
    def seed(value: int) -> None:
        """Re-seed Faker for reproducible data in a specific test."""
        Faker.seed(value)
        random.seed(value)


def _strong_password(length: int = 16) -> str:
    chars = string.ascii_letters + string.digits + "!@#$%^&*"
    pwd = [
        random.choice(string.ascii_uppercase),
        random.choice(string.ascii_lowercase),
        random.choice(string.digits),
        random.choice("!@#$%^&*"),
    ]
    pwd += random.choices(chars, k=length - 4)
    random.shuffle(pwd)
    return "".join(pwd)
