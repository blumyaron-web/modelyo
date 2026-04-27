"""
UI — End-to-end checkout test
Scenario 4: Add product → checkout flow → verify order-complete confirmation.
"""
from __future__ import annotations

import pytest
from playwright.sync_api import Page

from pages.cart_page import CartPage
from pages.checkout_page import (
    CheckoutCompletePage,
    CheckoutOverviewPage,
    CheckoutStepOnePage,
)
from pages.inventory_page import InventoryPage

PRODUCT = "Sauce Labs Fleece Jacket"
EXPECTED_CONFIRMATION_HEADER = "Thank you for your order!"


class TestCheckout:
    def test_end_to_end_checkout(self, logged_in_page: Page) -> None:
        """Scenario 4 — full checkout flow lands on order-complete page."""
        # 1. Add product
        inventory = InventoryPage(logged_in_page)
        inventory.add_item_to_cart_by_name(PRODUCT)

        # 2. Go to cart
        inventory.go_to_cart()
        CartPage(logged_in_page).wait_for_cart().proceed_to_checkout()

        # 3. Your Information
        step_one = CheckoutStepOnePage(logged_in_page)
        step_one.wait_for_step_one()
        step_one.fill_information(first_name="Jane", last_name="Doe", postal_code="10001")
        step_one.continue_to_overview()

        # 4. Overview
        CheckoutOverviewPage(logged_in_page).wait_for_overview().finish()

        # 5. Confirmation
        complete = CheckoutCompletePage(logged_in_page)
        complete.wait_for_confirmation()
        header = complete.confirmation_header()

        assert header == EXPECTED_CONFIRMATION_HEADER, (
            f"Confirmation header changed!\n"
            f"  Expected : {EXPECTED_CONFIRMATION_HEADER!r}\n"
            f"  Got      : {header!r}"
        )
