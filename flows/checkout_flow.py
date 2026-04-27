"""Checkout flow — drives the full checkout journey and asserts order confirmation.

Public API
----------
    complete_checkout(page, *, first_name, last_name, postal_code) -> str
    assert_order_confirmed(header, expected_header)                -> None  (soft assertion)
"""
from __future__ import annotations

import logging

from assertpy import assert_that, soft_assertions
from playwright.sync_api import Page

from pages.cart_page import CartPage
from pages.checkout_page import (
    CheckoutCompletePage,
    CheckoutOverviewPage,
    CheckoutStepOnePage,
)

logger = logging.getLogger(__name__)


# ── Actions ───────────────────────────────────────────────────────────────

def complete_checkout(
    page: Page,
    *,
    first_name: str,
    last_name: str,
    postal_code: str,
) -> str:
    """Drive the full checkout sequence and return the order-confirmation header.

    Steps:
        1. Proceed from cart to checkout step one.
        2. Fill in shopper information and continue.
        3. Finish on the overview page.
        4. Wait for and return the confirmation header text.

    Args:
        page:        Active Playwright page; must be on the cart page already.
        first_name:  Shopper first name.
        last_name:   Shopper last name.
        postal_code: Shopper postal / ZIP code.

    Returns:
        The confirmation header string, e.g. ``"Thank you for your order!"``.
    """
    logger.info("[checkout_flow] Starting checkout for %s %s", first_name, last_name)

    CartPage(page).wait_for_cart().proceed_to_checkout()

    step_one = CheckoutStepOnePage(page)
    step_one.wait_for_step_one()
    step_one.fill_information(first_name=first_name, last_name=last_name, postal_code=postal_code)
    step_one.continue_to_overview()

    CheckoutOverviewPage(page).wait_for_overview().finish()

    complete = CheckoutCompletePage(page)
    complete.wait_for_confirmation()
    header = complete.confirmation_header()
    logger.info("[checkout_flow] Order confirmation page reached — header: %r", header)
    return header


# ── Assertions ────────────────────────────────────────────────────────────

def assert_order_confirmed(header: str, expected_header: str) -> None:
    """Soft-assert the order-confirmation header matches the expected value verbatim.

    Checks:
        • Header is not empty (confirmation page actually rendered content).
        • Header text equals ``expected_header`` exactly (wording regressions
          are caught immediately).
    """
    logger.info("[checkout_flow] Asserting order confirmation header")

    with soft_assertions():
        assert_that(header) \
            .described_as(
                "Order confirmation header must not be empty — "
                "the confirmation page may not have loaded or the selector changed."
            ).is_not_empty()

        assert_that(header) \
            .described_as(
                f"Order confirmation header mismatch.\n"
                f"  Expected : {expected_header!r}\n"
                f"  Actual   : {header!r}\n"
                "The app copy may have changed — update EXPECTED_CONFIRMATION_HEADER "
                "if this is intentional."
            ).is_equal_to(expected_header)

    logger.info("[checkout_flow] Order confirmation assertions passed ✓")
