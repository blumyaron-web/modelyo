"""Cart flow — add-to-cart actions, cart navigation, and cart-specific assertions.

Public API
----------
    add_items_to_cart(inventory, products)          -> None
    open_cart(page, inventory)                      -> CartPage
    assert_cart_badge(inventory, expected_count)    -> None   (soft assertion)
    assert_cart_contents(cart, expected_products)   -> None   (soft assertions)
    assert_badge_increments(inventory, products)    -> None   (soft assertions)
    assert_badge_decrements(inventory, products)    -> None   (soft assertions)
"""
from __future__ import annotations

import logging

from assertpy import assert_that, soft_assertions
from playwright.sync_api import Page

from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage

logger = logging.getLogger(__name__)


# ── Actions ───────────────────────────────────────────────────────────────

def add_items_to_cart(inventory: InventoryPage, products: list[str]) -> None:
    """Click *Add to cart* for every product name in *products*."""
    logger.info("[cart_flow] Adding %d item(s) to cart: %s", len(products), products)
    for product in products:
        inventory.add_item_to_cart_by_name(product)


def open_cart(page: Page, inventory: InventoryPage) -> CartPage:
    """Click the cart icon and wait for the cart page to load."""
    logger.info("[cart_flow] Navigating to cart")
    inventory.go_to_cart()
    cart = CartPage(page)
    cart.wait_for_cart()
    logger.info("[cart_flow] Cart page loaded")
    return cart


# ── Assertions ────────────────────────────────────────────────────────────

def assert_cart_badge(inventory: InventoryPage, expected_count: int) -> None:
    """Soft-assert the cart badge reflects the expected item count.

    Checks:
        • Badge value equals ``expected_count``.
    """
    logger.info("[cart_flow] Asserting cart badge count == %d", expected_count)
    actual = inventory.cart_badge_count()

    with soft_assertions():
        assert_that(actual) \
            .described_as(
                f"Cart badge counter mismatch — "
                f"added {expected_count} item(s) but badge shows {actual}. "
                "The badge may not have updated or an 'Add to cart' click was missed."
            ).is_equal_to(expected_count)

    logger.info("[cart_flow] Cart badge assertion passed ✓")


def assert_cart_contents(cart: CartPage, expected_products: list[str]) -> None:
    """Soft-assert every expected product appears in the cart with a valid price.

    Checks (per product):
        • Product name is present in the cart item list.
    Checks (per price):
        • Price string starts with '$' (format: $XX.XX).
    """
    logger.info("[cart_flow] Asserting cart contains: %s", expected_products)
    cart_items = cart.cart_items()
    cart_names = [item["name"] for item in cart_items]
    cart_prices = [item["price"] for item in cart_items]

    with soft_assertions():
        for product in expected_products:
            assert_that(cart_names) \
                .described_as(
                    f"Product '{product}' missing from cart.\n"
                    f"  Cart currently contains: {cart_names}\n"
                    "Possible causes: 'Add to cart' did not register, or the item "
                    "was removed before navigating to the cart page."
                ).contains(product)

        for i, price in enumerate(cart_prices):
            assert_that(price) \
                .described_as(
                    f"Unexpected price format for cart item #{i + 1}.\n"
                    f"  Got      : {price!r}\n"
                    "  Expected : string starting with '$' (e.g. '$29.99'). "
                    "The price element selector or page structure may have changed."
                ).starts_with("$")

    logger.info("[cart_flow] Cart contents assertions passed ✓")


def assert_badge_increments(inventory: InventoryPage, products: list[str]) -> None:
    """Add each product one-by-one and soft-assert the badge increments correctly.

    Checks (after each add):
        • Badge count equals the running total of added products.
    """
    logger.info("[cart_flow] Asserting badge increments for %d product(s)", len(products))
    with soft_assertions():
        for i, product in enumerate(products, start=1):
            inventory.add_item_to_cart_by_name(product)
            actual = inventory.cart_badge_count()
            assert_that(actual) \
                .described_as(
                    f"Cart badge after adding '{product}' (item #{i}).\n"
                    f"  Expected : {i}\n"
                    f"  Actual   : {actual}\n"
                    "The badge did not increment — the 'Add to cart' action may have failed."
                ).is_equal_to(i)
    logger.info("[cart_flow] Badge increment assertions passed ✓")


def assert_badge_decrements(inventory: InventoryPage, products: list[str]) -> None:
    """Remove each product one-by-one and soft-assert the badge decrements correctly.

    Assumes all products in *products* are already in the cart.

    Checks (after each remove):
        • Badge count equals the remaining item total, OR
        • Badge is no longer visible when the cart is empty.
    """
    logger.info("[cart_flow] Asserting badge decrements for %d product(s)", len(products))
    with soft_assertions():
        for i, product in enumerate(products):
            inventory.remove_item_from_cart_by_name(product)
            expected = len(products) - (i + 1)

            if expected == 0:
                assert_that(inventory.cart_badge_visible()) \
                    .described_as(
                        "Cart badge should disappear when the cart is emptied — "
                        f"still visible after removing '{product}' (last item). "
                        "The badge element may not be hiding correctly."
                    ).is_false()
            else:
                actual = inventory.cart_badge_count()
                assert_that(actual) \
                    .described_as(
                        f"Cart badge after removing '{product}'.\n"
                        f"  Expected : {expected}\n"
                        f"  Actual   : {actual}\n"
                        "Badge did not decrement — the 'Remove' action may have failed."
                    ).is_equal_to(expected)

    logger.info("[cart_flow] Badge decrement assertions passed ✓")
