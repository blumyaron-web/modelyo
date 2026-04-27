"""Sort flow — product-sorting actions and assertions.

Public API
----------
    sort_and_get_prices(page, inventory, sort_value) -> list[float]
    assert_prices_ascending(prices)                 -> None   (soft assertions)
"""
from __future__ import annotations

import logging

from assertpy import assert_that, soft_assertions
from playwright.sync_api import Page

from pages.inventory_page import InventoryPage

logger = logging.getLogger(__name__)


# ── Actions ───────────────────────────────────────────────────────────────

def sort_and_get_prices(
    page: Page, inventory: InventoryPage, sort_value: str
) -> list[float]:
    """Apply a sort option and return all visible prices as floats.

    Args:
        page:       Active Playwright page (used to query price locators).
        inventory:  An already-loaded ``InventoryPage``.
        sort_value: Sort key accepted by the dropdown — ``'az'`` | ``'za'``
                    | ``'lohi'`` | ``'hilo'``.

    Returns:
        List of prices (as ``float``) in the DOM order after sorting.
    """
    logger.info("[sort_flow] Applying sort '%s'", sort_value)
    inventory.sort_by(sort_value)

    price_locators = page.locator('[data-test="inventory-item-price"]').all()
    prices: list[float] = []
    for loc in price_locators:
        text = loc.text_content() or ""
        prices.append(float(text.replace("$", "").strip()))

    logger.info("[sort_flow] Collected %d price(s): %s", len(prices), prices)
    return prices


# ── Assertions ────────────────────────────────────────────────────────────

def assert_prices_ascending(prices: list[float]) -> None:
    """Soft-assert that *prices* is a non-empty list in ascending order.

    Checks:
        • At least one price was found on the page (selector health check).
        • The list of prices equals its own sorted version (ascending order).
    """
    logger.info("[sort_flow] Asserting prices are in ascending order")

    with soft_assertions():
        assert_that(len(prices)) \
            .described_as(
                "Number of price elements found after sorting — "
                "expected >0 but found none. "
                "The '[data-test=\"inventory-item-price\"]' selector may have changed, "
                "or the inventory page did not fully render."
            ).is_greater_than(0)

        assert_that(prices) \
            .described_as(
                f"Product prices are not in ascending order after 'low → high' sort.\n"
                f"  Displayed order : {prices}\n"
                f"  Expected order  : {sorted(prices)}\n"
                "The sort feature may be broken or the price values were read "
                "before the DOM re-rendered."
            ).is_equal_to(sorted(prices))

    logger.info("[sort_flow] Price ascending assertions passed")
