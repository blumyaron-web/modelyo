"""
Central configuration — all values read from environment variables with
safe defaults.  No hardcoded URLs or credentials anywhere else in the codebase.
"""
from __future__ import annotations

import os


class Config:
    # ── Web ───────────────────────────────────────────────────────────────
    BASE_URL: str = os.getenv("BASE_URL", "https://www.saucedemo.com")
    STANDARD_USER: str = os.getenv("STANDARD_USER", "standard_user")
    PASSWORD: str = os.getenv("PASSWORD", "secret_sauce")

    # ── API ───────────────────────────────────────────────────────────────
    API_BASE_URL: str = os.getenv("API_BASE_URL", "https://jsonplaceholder.typicode.com")
    API_TIMEOUT: int = int(os.getenv("API_TIMEOUT", "10"))          # seconds

    # ── Browser / Playwright ──────────────────────────────────────────────
    BROWSER: str = os.getenv("BROWSER", "chromium")                 # chromium | firefox | webkit
    HEADLESS: bool = os.getenv("HEADLESS", "true").lower() == "true"
    SLOW_MO: int = int(os.getenv("SLOW_MO", "0"))                   # ms
    VIEWPORT_WIDTH: int = int(os.getenv("VIEWPORT_WIDTH", "1280"))
    VIEWPORT_HEIGHT: int = int(os.getenv("VIEWPORT_HEIGHT", "720"))

    # ── Playwright timeouts (all in ms) ───────────────────────────────────
    DEFAULT_TIMEOUT: int = int(os.getenv("DEFAULT_TIMEOUT", "10000"))
    NAVIGATION_TIMEOUT: int = int(os.getenv("NAVIGATION_TIMEOUT", "30000"))

    # ── Parallelism ───────────────────────────────────────────────────────
    WORKERS: int = int(os.getenv("WORKERS", "2"))


cfg = Config()
