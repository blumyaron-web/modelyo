"""
UI — Cart tests
Scenario 3: Add ≥2 distinct products, verify badge count and cart contents (name + price).
"""
from __future__ import annotations

import pytest
from playwright.sync_api import Page

from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage

# Products chosen by their exact display name on Swag Labs
PRODUCTS = [
    "Sauce Labs Backpack",
    "Sauce Labs Bike Light",
]


class TestCart:
    def test_add_two_items_and_verify_cart(self, logged_in_page: Page) -> None:
        """Scenario 3 — badge count and cart contents match what was added."""
        inventory = InventoryPage(logged_in_page)

        for product in PRODUCTS:
            inventory.add_item_to_cart_by_name(product)

        # Verify badge immediately after adding (Playwright auto-waits)
        badge_count = inventory.cart_badge_count()
        assert badge_count == len(PRODUCTS), (
            f"Cart badge should show {len(PRODUCTS)}, got {badge_count}"
        )

        # Navigate to cart and verify contents
        inventory.go_to_cart()
        cart = CartPage(logged_in_page)
        cart.wait_for_cart()
        cart_items = cart.cart_items()

        cart_names = [item["name"] for item in cart_items]
        cart_prices = [item["price"] for item in cart_items]

        for product in PRODUCTS:
            assert product in cart_names, f"'{product}' not found in cart: {cart_names}"

        # Prices must be non-empty strings (format: "$XX.XX")
        for price in cart_prices:
            assert price.startswith("$"), f"Unexpected price format: {price!r}"
