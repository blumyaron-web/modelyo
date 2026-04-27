"""
UI — Cart tests
Scenario 3: Add ≥2 distinct products, verify badge count and cart contents (name + price).
"""
from __future__ import annotations

import pytest
from playwright.sync_api import Page

from flows.cart_flow import (
    add_items_to_cart,
    assert_cart_badge,
    assert_cart_contents,
    open_cart,
)
from pages.inventory_page import InventoryPage

pytestmark = [
    pytest.mark.ui,
    pytest.mark.playwright,
    pytest.mark.cart,
    pytest.mark.regression,
]

# Products chosen by their exact display name on Swag Labs
PRODUCTS = [
    "Sauce Labs Backpack",
    "Sauce Labs Bike Light",
]


class TestCart:
    @pytest.mark.smoke
    def test_add_two_items_and_verify_cart(self, logged_in_page: Page) -> None:
        """Scenario 3 — badge count and cart contents match what was added."""
        inventory = InventoryPage(logged_in_page)

        add_items_to_cart(inventory, PRODUCTS)
        assert_cart_badge(inventory, expected_count=len(PRODUCTS))

        cart = open_cart(logged_in_page, inventory)
        assert_cart_contents(cart, expected_products=PRODUCTS)
