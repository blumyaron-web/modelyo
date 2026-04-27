"""
UI — Bonus tests (optional scenarios)
B1: Product sort — price low-to-high: verify item order matches ascending price.
B2: Cart badge updates correctly as items are added and removed.
"""
from __future__ import annotations

import pytest

from flows.flows import Flows
from tests.data.test_run_data import TestRunData

pytestmark = [
    pytest.mark.ui,
    pytest.mark.playwright,
    pytest.mark.bonus,
    pytest.mark.regression,
]


class TestSorting:
    @pytest.mark.catalog
    def test_sort_price_low_to_high(self, flows: Flows, test_run_data: TestRunData) -> None:
        """B1 — After sorting low→high, displayed prices must be in ascending order."""
        flows.sort_and_get_prices(sort_value=test_run_data.sort.price_low_to_high)
        flows.assert_prices_ascending()


class TestCartBadge:
    @pytest.mark.cart
    def test_badge_increments_and_decrements(self, flows: Flows, test_run_data: TestRunData) -> None:
        """B2 — Badge count tracks add/remove operations accurately."""
        flows.assert_badge_increments(list(test_run_data.cart.badge_cycle_products))
        flows.assert_badge_decrements(list(test_run_data.cart.badge_cycle_products))
