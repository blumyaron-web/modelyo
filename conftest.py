"""
Shared pytest fixtures and plugin configuration.

Fixture scopes at a glance:
  browser_context  — function scope  → each test gets a fresh context (isolated cookies/storage)
  page             — function scope  → fresh Playwright page per test
  logged_in_page   — function scope  → page already authenticated; avoids repeating login steps
  api_client       — function scope  → fresh APIClient per test (stateless HTTP, cheap to create)

Failure hooks:
  On any UI test failure we automatically capture:
    • full-page screenshot
    • page DOM (HTML)
    • Playwright trace  (started for every test, saved only on failure)
  Artifacts are written to the pytest tmp path and attached as pytest extras
  (visible in pytest-html / Allure reports).
"""
from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Generator

import pytest
from playwright.sync_api import (
    Browser,
    BrowserContext,
    Page,
    Playwright,
    sync_playwright,
)

from clients.api_client import APIClient
from config.config import cfg
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage
from tests.data.test_run_data import TestRunData

logger = logging.getLogger(__name__)

# ── Artifacts directory (used by GitHub Actions upload-artifact) ───────────
ARTIFACT_DIR = Path(os.getenv("ARTIFACT_DIR", "test-artifacts"))
ARTIFACT_DIR.mkdir(parents=True, exist_ok=True)

# ── Playwright lifecycle ───────────────────────────────────────────────────


@pytest.fixture(scope="session")
def playwright_instance() -> Generator[Playwright, None, None]:
    with sync_playwright() as pw:
        yield pw


@pytest.fixture(scope="session")
def browser(playwright_instance: Playwright) -> Generator[Browser, None, None]:
    browser_type = getattr(playwright_instance, cfg.BROWSER)
    b = browser_type.launch(headless=cfg.HEADLESS, slow_mo=cfg.SLOW_MO)
    logger.info("Browser launched: %s  headless=%s", cfg.BROWSER, cfg.HEADLESS)
    yield b
    b.close()


@pytest.fixture()
def browser_context(browser: Browser) -> Generator[BrowserContext, None, None]:
    """Fresh isolated browser context per test — no shared cookies or storage."""
    ctx = browser.new_context(
        viewport={"width": cfg.VIEWPORT_WIDTH, "height": cfg.VIEWPORT_HEIGHT},
    )
    ctx.tracing.start(screenshots=True, snapshots=True, sources=True)
    yield ctx
    ctx.tracing.stop()   # discard trace (saved only on failure via the hook)
    ctx.close()


@pytest.fixture()
def page(browser_context: BrowserContext) -> Generator[Page, None, None]:
    p = browser_context.new_page()
    yield p
    p.close()


@pytest.fixture()
def logged_in_page(page: Page) -> Page:
    """Return a page that is already logged in as standard_user."""
    login = LoginPage(page)
    login.open()
    login.login(cfg.STANDARD_USER, cfg.PASSWORD)
    InventoryPage(page).wait_for_inventory()
    return page


# ── API ───────────────────────────────────────────────────────────────────


@pytest.fixture()
def api_client() -> Generator[APIClient, None, None]:
    with APIClient() as client:
        yield client


@pytest.fixture()
def test_run_data() -> TestRunData:
    """Injectable test-data object; access via domain namespaces.

    Examples::

        test_run_data.checkout.product
        test_run_data.cart.products
        test_run_data.posts.create_payload
    """
    return TestRunData()


# ── Failure artifact hook ─────────────────────────────────────────────────


@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    if report.when == "call" and report.failed:
        # Only applicable to UI tests that have a `page` fixture
        page: Page | None = item.funcargs.get("page") or item.funcargs.get(
            "logged_in_page"
        )
        ctx: BrowserContext | None = item.funcargs.get("browser_context")

        if page is None:
            return

        safe_name = item.nodeid.replace("/", "_").replace("::", "__").replace(" ", "_")

        # Screenshot
        screenshot_path = ARTIFACT_DIR / f"{safe_name}.png"
        try:
            page.screenshot(path=str(screenshot_path), full_page=True)
            logger.error("Failure screenshot saved: %s", screenshot_path)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not capture screenshot: %s", exc)

        # DOM
        dom_path = ARTIFACT_DIR / f"{safe_name}.html"
        try:
            dom_path.write_text(page.content(), encoding="utf-8")
            logger.error("Failure DOM saved: %s", dom_path)
        except Exception as exc:  # noqa: BLE001
            logger.warning("Could not capture DOM: %s", exc)

        # Playwright trace
        if ctx is not None:
            trace_path = ARTIFACT_DIR / f"{safe_name}.zip"
            try:
                # Re-stop with export — we need a new context stop call
                ctx.tracing.stop(path=str(trace_path))
                logger.error("Failure trace saved: %s", trace_path)
            except Exception as exc:  # noqa: BLE001
                logger.warning("Could not save trace: %s", exc)
