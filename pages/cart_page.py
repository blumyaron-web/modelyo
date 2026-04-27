"""Cart page."""
from __future__ import annotations

import logging
from typing import TypedDict

from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class CartItem(TypedDict):
    name: str
    price: str


class CartPage(BasePage):
    _CART_CONTENTS = "cart-contents-container"   # data-test
    _CART_ITEM = "inventory-item"                # data-test (reused on cart)
    _ITEM_NAME = "inventory-item-name"           # data-test
    _ITEM_PRICE = "inventory-item-price"         # data-test
    _CHECKOUT_BUTTON = "checkout"                # data-test

    def wait_for_cart(self) -> "CartPage":
        self.get_by_test_id(self._CART_CONTENTS).wait_for(state="visible")
        logger.info("Cart page loaded")
        return self

    def cart_items(self) -> list[CartItem]:
        items = self.get_by_test_id(self._CART_ITEM).all()
        result: list[CartItem] = []
        for item in items:
            name = item.locator(f'[data-test="{self._ITEM_NAME}"]').text_content() or ""
            price = item.locator(f'[data-test="{self._ITEM_PRICE}"]').text_content() or ""
            result.append({"name": name.strip(), "price": price.strip()})
            logger.debug("Cart item: name=%r price=%r", name, price)
        return result

    def proceed_to_checkout(self) -> None:
        logger.info("Clicking checkout button")
        self.get_by_test_id(self._CHECKOUT_BUTTON).click()
