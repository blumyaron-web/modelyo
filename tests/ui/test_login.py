"""
UI — Login tests
Scenario 1: Happy path  → lands on inventory page, items visible.
Scenario 2: Invalid creds → error message matches the exact app text.
"""
from __future__ import annotations

import pytest

from config.config import cfg
from flows.flows import Flows
from tests.data.test_run_data import TestRunData

pytestmark = [
    pytest.mark.ui,
    pytest.mark.playwright,
    pytest.mark.authentication,
    pytest.mark.smoke,
]


class TestLogin:
    @pytest.mark.regression
    def test_happy_path(self, flows_unauthenticated: Flows, test_run_data: TestRunData) -> None:
        """Scenario 1 — valid credentials land on a populated inventory page."""
        flows_unauthenticated.perform_login(username=cfg.STANDARD_USER, password=cfg.PASSWORD)
        flows_unauthenticated.assert_login_success()

    @pytest.mark.regression
    @pytest.mark.boundary
    def test_invalid_credentials(self, flows_unauthenticated: Flows, test_run_data: TestRunData) -> None:
        """Scenario 2 — wrong password surfaces the exact error string."""
        flows_unauthenticated.perform_failed_login(username=cfg.STANDARD_USER, password=test_run_data.login.wrong_password)
        flows_unauthenticated.assert_login_error(expected_error=test_run_data.login.invalid_credentials_error)
