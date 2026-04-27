"""
UI — End-to-end checkout test
Scenario 4: Add product → checkout flow → verify order-complete confirmation.
"""
from __future__ import annotations

import pytest
from playwright.sync_api import Page

from flows.cart_flow import add_items_to_cart, open_cart
from flows.checkout_flow import assert_order_confirmed, complete_checkout
from pages.inventory_page import InventoryPage

pytestmark = [
    pytest.mark.ui,
    pytest.mark.playwright,
    pytest.mark.checkout,
    pytest.mark.e2e,
    pytest.mark.smoke,
]

PRODUCT = "Sauce Labs Fleece Jacket"
EXPECTED_CONFIRMATION_HEADER = "Thank you for your order!"


class TestCheckout:
    @pytest.mark.regression
    def test_end_to_end_checkout(self, logged_in_page: Page) -> None:
        """Scenario 4 — full checkout flow lands on the order-complete page."""
        inventory = InventoryPage(logged_in_page)
        add_items_to_cart(inventory, [PRODUCT])
        open_cart(logged_in_page, inventory)

        header = complete_checkout(
            logged_in_page,
            first_name="Jane",
            last_name="Doe",
            postal_code="10001",
        )
        assert_order_confirmed(header, expected_header=EXPECTED_CONFIRMATION_HEADER)
