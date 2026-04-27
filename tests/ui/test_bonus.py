"""
UI — Bonus tests (optional scenarios)
B1: Product sort — price low-to-high: verify item order matches ascending price.
B2: Cart badge updates correctly as items are added and removed.
"""
from __future__ import annotations

import pytest
from playwright.sync_api import Page

from flows.cart_flow import assert_badge_decrements, assert_badge_increments
from flows.sort_flow import assert_prices_ascending, sort_and_get_prices
from pages.inventory_page import InventoryPage

pytestmark = [
    pytest.mark.ui,
    pytest.mark.playwright,
    pytest.mark.bonus,
    pytest.mark.regression,
]


class TestSorting:
    @pytest.mark.catalog
    def test_sort_price_low_to_high(self, logged_in_page: Page) -> None:
        """B1 — After sorting low→high, displayed prices must be in ascending order."""
        inventory = InventoryPage(logged_in_page)
        prices = sort_and_get_prices(logged_in_page, inventory, sort_value="lohi")
        assert_prices_ascending(prices)


class TestCartBadge:
    @pytest.mark.cart
    def test_badge_increments_and_decrements(self, logged_in_page: Page) -> None:
        """B2 — Badge count tracks add/remove operations accurately."""
        inventory = InventoryPage(logged_in_page)
        products = ["Sauce Labs Backpack", "Sauce Labs Bike Light", "Sauce Labs Onesie"]

        assert_badge_increments(inventory, products)
        assert_badge_decrements(inventory, products)
