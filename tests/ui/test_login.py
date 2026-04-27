"""
UI — Login tests
Scenario 1: Happy path  → lands on inventory page, items visible
Scenario 2: Invalid creds → error message matches the exact app text
"""
from __future__ import annotations

import pytest
from playwright.sync_api import Page

from config.config import cfg
from pages.inventory_page import InventoryPage
from pages.login_page import LoginPage

# The exact wording the app renders — test fails loudly if it changes.
EXPECTED_ERROR = "Epic sadface: Username and password do not match any user in this service"


class TestLogin:
    def test_happy_path(self, page: Page) -> None:
        """Scenario 1 — valid credentials land on the inventory page."""
        login = LoginPage(page)
        login.open()
        login.login(cfg.STANDARD_USER, cfg.PASSWORD)

        inventory = InventoryPage(page)
        inventory.wait_for_inventory()

        assert inventory.is_loaded(), "Inventory container should be visible after login"
        items = inventory.inventory_items()
        assert len(items) > 0, "At least one inventory item should be present"

    def test_invalid_credentials(self, page: Page) -> None:
        """Scenario 2 — wrong password shows the exact error string."""
        login = LoginPage(page)
        login.open()
        login.login(cfg.STANDARD_USER, "wrong_password_xyz")

        error_text = login.error_message()

        # Exact-match assertion: the test description says "fail loudly if wording changes"
        assert error_text == EXPECTED_ERROR, (
            f"Error message changed!\n"
            f"  Expected : {EXPECTED_ERROR!r}\n"
            f"  Got      : {error_text!r}"
        )
