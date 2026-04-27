"""Checkout test data."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class CheckoutData:
    # Product added to the cart before starting the checkout flow.
    product: str = "Sauce Labs Fleece Jacket"

    # Shopper information filled in on the checkout step-one form.
    first_name: str = "Jane"
    last_name: str = "Doe"
    postal_code: str = "10001"

    # Exact confirmation header rendered on the order-complete page.
    confirmation_header: str = "Thank you for your order!"


# ── Module-level constants (kept for backward compatibility) ───────────────
_defaults = CheckoutData()
CHECKOUT_PRODUCT: str = _defaults.product
SHOPPER_FIRST_NAME: str = _defaults.first_name
SHOPPER_LAST_NAME: str = _defaults.last_name
SHOPPER_POSTAL_CODE: str = _defaults.postal_code
ORDER_CONFIRMATION_HEADER: str = _defaults.confirmation_header
