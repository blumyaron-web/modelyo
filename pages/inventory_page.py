"""Inventory / product-listing page."""
from __future__ import annotations

import logging

from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class InventoryPage(BasePage):
    _INVENTORY_CONTAINER = "inventory-container"   # data-test
    _INVENTORY_ITEM = "inventory-item"             # data-test (each card)
    _CART_BADGE = "shopping-cart-badge"            # data-test
    _CART_LINK = "shopping-cart-link"              # data-test
    _SORT_CONTAINER = "product-sort-container"     # data-test

    # ── Navigation / state ────────────────────────────────────────────────

    def wait_for_inventory(self) -> "InventoryPage":
        self.get_by_test_id(self._INVENTORY_CONTAINER).wait_for(state="visible")
        logger.info("Inventory page loaded")
        return self

    def is_loaded(self) -> bool:
        return self.get_by_test_id(self._INVENTORY_CONTAINER).is_visible()

    # ── Products ──────────────────────────────────────────────────────────

    def inventory_items(self):
        """Return all inventory item locators."""
        return self.get_by_test_id(self._INVENTORY_ITEM).all()

    def add_item_to_cart_by_name(self, name: str) -> None:
        """Click the 'Add to cart' button for a product with the given name."""
        # data-test pattern: add-to-cart-<slug>  e.g. add-to-cart-sauce-labs-backpack
        slug = name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace(".", "")
        test_id = f"add-to-cart-{slug}"
        logger.info("Adding item to cart: %s (test-id: %s)", name, test_id)
        self.get_by_test_id(test_id).click()

    def remove_item_from_cart_by_name(self, name: str) -> None:
        slug = name.lower().replace(" ", "-").replace("(", "").replace(")", "").replace(".", "")
        test_id = f"remove-{slug}"
        logger.info("Removing item from cart: %s", name)
        self.get_by_test_id(test_id).click()

    # ── Cart badge ────────────────────────────────────────────────────────

    def cart_badge_count(self) -> int:
        badge = self.get_by_test_id(self._CART_BADGE)
        badge.wait_for(state="visible")
        return int(badge.text_content() or "0")

    def cart_badge_visible(self) -> bool:
        return self.get_by_test_id(self._CART_BADGE).is_visible()

    # ── Navigation ────────────────────────────────────────────────────────

    def go_to_cart(self) -> None:
        logger.info("Opening cart")
        self.get_by_test_id(self._CART_LINK).click()

    # ── Sorting (bonus) ───────────────────────────────────────────────────

    def sort_by(self, value: str) -> None:
        """value: 'az' | 'za' | 'lohi' | 'hilo'"""
        logger.info("Sorting products by '%s'", value)
        self.get_by_test_id(self._SORT_CONTAINER).select_option(value)
