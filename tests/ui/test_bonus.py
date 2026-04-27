"""
UI — Bonus tests (optional scenarios)
B1: Product sort — price low-to-high: verify item order matches ascending price.
B2: Cart badge updates correctly as items are added and removed.
"""
from __future__ import annotations

import pytest
from playwright.sync_api import Page

from pages.inventory_page import InventoryPage

pytestmark = pytest.mark.bonus


class TestSorting:
    def test_sort_price_low_to_high(self, logged_in_page: Page) -> None:
        """B1 — After sorting lohi, displayed prices must be in ascending order."""
        inventory = InventoryPage(logged_in_page)
        inventory.sort_by("lohi")

        # Collect all price elements in DOM order after sort
        price_locators = logged_in_page.locator('[data-test="inventory-item-price"]').all()
        prices = []
        for loc in price_locators:
            text = loc.text_content() or ""
            prices.append(float(text.replace("$", "").strip()))

        assert prices == sorted(prices), (
            f"Prices are not in ascending order after sort: {prices}"
        )
        assert len(prices) > 0, "No price elements found on inventory page"


class TestCartBadge:
    def test_badge_increments_and_decrements(self, logged_in_page: Page) -> None:
        """B2 — Badge count tracks add/remove accurately."""
        inventory = InventoryPage(logged_in_page)

        products = ["Sauce Labs Backpack", "Sauce Labs Bike Light", "Sauce Labs Onesie"]

        # Add one by one, verify badge increments
        for i, product in enumerate(products, start=1):
            inventory.add_item_to_cart_by_name(product)
            count = inventory.cart_badge_count()
            assert count == i, f"Badge should be {i} after adding '{product}', got {count}"

        # Remove one by one, verify badge decrements
        for i, product in enumerate(products):
            inventory.remove_item_from_cart_by_name(product)
            expected = len(products) - (i + 1)
            if expected == 0:
                # Badge disappears entirely when cart is empty
                assert not inventory.cart_badge_visible(), "Badge should disappear when cart is empty"
            else:
                count = inventory.cart_badge_count()
                assert count == expected, (
                    f"Badge should be {expected} after removing '{product}', got {count}"
                )
