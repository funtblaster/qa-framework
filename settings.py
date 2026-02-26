"""
config/settings.py
──────────────────
Central configuration loaded from environment variables or .env files.
All settings are typed via Pydantic Settings.

Usage:
    from config.settings import settings

    print(settings.base_url)
    print(settings.api_base_url)
"""

from __future__ import annotations

from enum import Enum
from pathlib import Path

from pydantic import Field, HttpUrl, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

ROOT_DIR = Path(__file__).parent.parent


class Environment(str, Enum):
    LOCAL = "local"
    STAGING = "staging"
    PRODUCTION = "production"


class Browser(str, Enum):
    CHROMIUM = "chromium"
    FIREFOX = "firefox"
    WEBKIT = "webkit"


class Settings(BaseSettings):
    """
    All settings can be overridden by environment variables or a .env file.

    Priority (highest → lowest):
        1. Shell environment variables
        2. .env file in project root
        3. Default values below
    """

    model_config = SettingsConfigDict(
        env_file=ROOT_DIR / ".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore",
    )

    # ── Environment ──────────────────────────────────────────────────────────
    test_env: Environment = Field(Environment.LOCAL, description="Target environment")

    # ── URLs ─────────────────────────────────────────────────────────────────
    base_url: str = Field("http://localhost:3000", description="Website base URL")
    api_base_url: str = Field("http://localhost:3000", description="API base URL")

    # ── Auth ─────────────────────────────────────────────────────────────────
    test_username: str = Field("", description="Test account username / email")
    test_password: str = Field("", description="Test account password")
    api_token: str = Field("", description="Bearer token for API auth (if applicable)")

    # ── Browser ───────────────────────────────────────────────────────────────
    browser: Browser = Field(Browser.CHROMIUM, description="Playwright browser")
    headless: bool = Field(True, description="Run browser in headless mode")
    slow_mo: int = Field(0, description="Playwright slow-motion delay in ms")
    viewport_width: int = Field(1280, description="Browser viewport width")
    viewport_height: int = Field(720, description="Browser viewport height")

    # ── HTTP Client ───────────────────────────────────────────────────────────
    request_timeout: int = Field(30, description="HTTP request timeout in seconds")
    verify_ssl: bool = Field(True, description="Verify SSL certificates")

    # ── Test Behaviour ────────────────────────────────────────────────────────
    screenshot_on_failure: bool = Field(True, description="Capture screenshot on UI test failure")
    video_on_failure: bool = Field(False, description="Record video on UI test failure")
    trace_on_failure: bool = Field(True, description="Capture Playwright trace on failure")

    # ── Retry ─────────────────────────────────────────────────────────────────
    max_retries: int = Field(3, description="Max retries for flaky operations")
    retry_delay: float = Field(1.0, description="Delay between retries in seconds")

    @field_validator("base_url", "api_base_url", mode="before")
    @classmethod
    def strip_trailing_slash(cls, v: str) -> str:
        return v.rstrip("/")

    @property
    def is_production(self) -> bool:
        return self.test_env == Environment.PRODUCTION

    @property
    def auth_headers(self) -> dict[str, str]:
        if self.api_token:
            return {"Authorization": f"Bearer {self.api_token}"}
        return {}


# Singleton instance — import this throughout the framework
settings = Settings()
