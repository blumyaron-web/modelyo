"""Checkout pages — step one (Your Information), overview, and confirmation."""
from __future__ import annotations

import logging

from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class CheckoutStepOnePage(BasePage):
    _FIRST_NAME = "firstName"           # data-test
    _LAST_NAME = "lastName"             # data-test
    _POSTAL_CODE = "postalCode"         # data-test
    _CONTINUE = "continue"              # data-test
    _CHECKOUT_INFO = "checkout-info-container"  # data-test

    def wait_for_step_one(self) -> "CheckoutStepOnePage":
        self.get_by_test_id(self._CHECKOUT_INFO).wait_for(state="visible")
        logger.info("Checkout step-one loaded")
        return self

    def fill_information(
        self, first_name: str, last_name: str, postal_code: str
    ) -> None:
        logger.info("Filling checkout information")
        self.get_by_test_id(self._FIRST_NAME).fill(first_name)
        self.get_by_test_id(self._LAST_NAME).fill(last_name)
        self.get_by_test_id(self._POSTAL_CODE).fill(postal_code)

    def continue_to_overview(self) -> None:
        logger.info("Clicking Continue")
        self.get_by_test_id(self._CONTINUE).click()


class CheckoutOverviewPage(BasePage):
    _OVERVIEW = "checkout-summary-container"   # data-test
    _FINISH = "finish"                         # data-test

    def wait_for_overview(self) -> "CheckoutOverviewPage":
        self.get_by_test_id(self._OVERVIEW).wait_for(state="visible")
        logger.info("Checkout overview loaded")
        return self

    def finish(self) -> None:
        logger.info("Clicking Finish")
        self.get_by_test_id(self._FINISH).click()


class CheckoutCompletePage(BasePage):
    _COMPLETE_HEADER = "complete-header"       # data-test
    _COMPLETE_CONTAINER = "checkout-complete-container"  # data-test

    def wait_for_confirmation(self) -> "CheckoutCompletePage":
        self.get_by_test_id(self._COMPLETE_CONTAINER).wait_for(state="visible")
        logger.info("Order confirmation page loaded")
        return self

    def confirmation_header(self) -> str:
        text = self.get_by_test_id(self._COMPLETE_HEADER).text_content() or ""
        logger.info("Confirmation header: %r", text)
        return text.strip()
