"""Login flow — navigation, authentication, and login-specific assertions.

Public API
----------
    perform_login(page, username, password)  -> InventoryPage
    perform_failed_login(page, username, password) -> LoginPage
    assert_login_success(inventory)          -> None   (soft assertions)
    assert_login_error(login_page, expected) -> None   (soft assertion)
"""
from __future__ import annotations

import logging

from assertpy import assert_that, soft_assertions
from playwright.sync_api import Page

from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

logger = logging.getLogger(__name__)


# ── Actions ───────────────────────────────────────────────────────────────

def perform_login(page: Page, username: str, password: str) -> InventoryPage:
    """Open the login page, submit valid credentials, and wait for the inventory.

    Returns:
        An ``InventoryPage`` that has already waited for the inventory container.

    Raises:
        playwright.sync_api.TimeoutError: Login failed — inventory never appeared.
    """
    logger.info("[login_flow] Logging in as '%s'", username)
    login = LoginPage(page)
    login.open()
    login.login(username, password)

    inventory = InventoryPage(page)
    inventory.wait_for_inventory()
    logger.info("[login_flow] Login successful — inventory page loaded")
    return inventory


def perform_failed_login(page: Page, username: str, password: str) -> LoginPage:
    """Submit credentials that are expected to fail; stay on the login page.

    Returns:
        The ``LoginPage`` instance so the caller can query the error state.
    """
    logger.info("[login_flow] Attempting failed login as '%s'", username)
    login = LoginPage(page)
    login.open()
    login.login(username, password)
    logger.info("[login_flow] Credentials submitted — expecting error message")
    return login


# ── Assertions ────────────────────────────────────────────────────────────

def assert_login_success(inventory: InventoryPage) -> None:
    """Soft-assert that a successful login landed on a populated inventory page.

    Checks:
        • Inventory container is visible.
        • At least one product item is rendered.

    All failures are collected before raising so the report shows every
    broken assertion in a single test run.
    """
    logger.info("[login_flow] Asserting successful login state")
    items = inventory.inventory_items()

    with soft_assertions():
        assert_that(inventory.is_loaded()) \
            .described_as(
                "Inventory container visibility after login — "
                "the page should transition away from /login to /inventory"
            ).is_true()

        assert_that(len(items)) \
            .described_as(
                f"Number of product items on the inventory page — "
                f"expected >0 but found {len(items)}; "
                "the catalogue may be empty or the page did not fully load"
            ).is_greater_than(0)

    logger.info("[login_flow] Login success assertions passed ✓")


def assert_login_error(login_page: LoginPage, expected_error: str) -> None:
    """Soft-assert that the login page shows the expected error text verbatim.

    Checks:
        • An error container is visible.
        • The error text matches ``expected_error`` exactly (wording changes
          in the app will be caught immediately).
    """
    logger.info("[login_flow] Asserting login error message")
    actual = login_page.error_message()

    with soft_assertions():
        assert_that(login_page.is_error_visible()) \
            .described_as(
                "Error message container visibility — "
                "submitting invalid credentials must show the error banner"
            ).is_true()

        assert_that(actual) \
            .described_as(
                f"Login error message text mismatch.\n"
                f"  Expected : {expected_error!r}\n"
                f"  Actual   : {actual!r}\n"
                "The app wording may have changed — update EXPECTED_ERROR if intentional."
            ).is_equal_to(expected_error)

    logger.info("[login_flow] Login error assertions passed ✓")
