"""
UI — End-to-end checkout test
Scenario 4: Add product → checkout flow → verify order-complete confirmation.
"""
from __future__ import annotations

import pytest

from flows.flows import Flows
from tests.data.test_run_data import TestRunData

pytestmark = [
    pytest.mark.ui,
    pytest.mark.playwright,
    pytest.mark.checkout,
    pytest.mark.e2e,
    pytest.mark.smoke,
]


class TestCheckout:
    @pytest.mark.regression
    def test_end_to_end_checkout(self, flows: Flows, test_run_data: TestRunData) -> None:
        """Scenario 4 — full checkout flow lands on the order-complete page."""
        flows.add_items_to_cart([test_run_data.checkout.product])
        flows.open_cart()

        flows.complete_checkout(
            first_name=test_run_data.checkout.first_name,
            last_name=test_run_data.checkout.last_name,
            postal_code=test_run_data.checkout.postal_code,
        )
        flows.assert_order_confirmed(expected_header=test_run_data.checkout.confirmation_header)
