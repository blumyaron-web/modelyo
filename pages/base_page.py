"""
Base Page — every page object inherits from here.
Centralises:
  • Playwright page reference
  • Timeout constants from config
  • Common navigation helpers
  • Screenshot / DOM capture helpers (called automatically on failure)
  • Structured logging
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from config.config import cfg

if TYPE_CHECKING:
    from playwright.sync_api import Page, Locator

logger = logging.getLogger(__name__)


class BasePage:
    def __init__(self, page: "Page") -> None:
        self._page = page
        self._page.set_default_timeout(cfg.DEFAULT_TIMEOUT)
        self._page.set_default_navigation_timeout(cfg.NAVIGATION_TIMEOUT)

    # ── Navigation ────────────────────────────────────────────────────────

    def goto(self, path: str = "") -> None:
        url = f"{cfg.BASE_URL}{path}"
        logger.info("Navigating to %s", url)
        self._page.goto(url, wait_until="domcontentloaded")

    # ── Locator helpers ───────────────────────────────────────────────────

    def locator(self, selector: str) -> "Locator":
        return self._page.locator(selector)

    def get_by_test_id(self, test_id: str) -> "Locator":
        """Prefer data-test attributes — most stable selector strategy.
        Swag Labs uses 'data-test' (not the Playwright default 'data-testid').
        """
        return self._page.locator(f'[data-test="{test_id}"]')

    def get_by_role(self, role: str, **kwargs) -> "Locator":
        return self._page.get_by_role(role, **kwargs)

    # ── Diagnostics ───────────────────────────────────────────────────────

    def take_screenshot(self, name: str) -> bytes:
        logger.debug("Taking screenshot: %s", name)
        return self._page.screenshot(path=name, full_page=True)

    def get_dom(self) -> str:
        return self._page.content()

    @property
    def page(self) -> "Page":
        return self._page
