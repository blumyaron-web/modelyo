"""
UI — Cart tests
Scenario 3: Add ≥2 distinct products, verify badge count and cart contents (name + price).
"""
from __future__ import annotations

import pytest

from flows.flows import Flows
from tests.data.test_run_data import TestRunData

pytestmark = [
    pytest.mark.ui,
    pytest.mark.playwright,
    pytest.mark.cart,
    pytest.mark.regression,
]


class TestCart:
    @pytest.mark.smoke
    def test_add_two_items_and_verify_cart(self, flows: Flows, test_run_data: TestRunData) -> None:
        """Scenario 3 — badge count and cart contents match what was added."""
        flows.add_items_to_cart(list(test_run_data.cart.products))
        flows.assert_cart_badge(expected_count=len(test_run_data.cart.products))

        flows.open_cart()
        flows.assert_cart_contents(expected_products=list(test_run_data.cart.products))
