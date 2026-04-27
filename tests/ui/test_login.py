"""
UI — Login tests
Scenario 1: Happy path  → lands on inventory page, items visible.
Scenario 2: Invalid creds → error message matches the exact app text.
"""
from __future__ import annotations

import pytest
from playwright.sync_api import Page

from config.config import cfg
from flows.flows import Flows
from tests.data.test_run_data import TestRunData

pytestmark = [
    pytest.mark.ui,
    pytest.mark.playwright,
    pytest.mark.authentication,
    pytest.mark.smoke,
]


# ── Fixture override ──────────────────────────────────────────────────────
# Login tests need an *unauthenticated* page so they can drive login themselves.
# This module-level fixture shadows the ui/conftest.py ``flows`` fixture.
@pytest.fixture()
def flows(page: Page) -> Flows:
    """Flows backed by a fresh, unauthenticated page for login testing."""
    return Flows(page=page)


# ── Tests ─────────────────────────────────────────────────────────────────

class TestLogin:
    @pytest.mark.regression
    def test_happy_path(self, flows: Flows, test_run_data: TestRunData) -> None:
        """Scenario 1 — valid credentials land on a populated inventory page."""
        flows.perform_login(username=cfg.STANDARD_USER, password=cfg.PASSWORD)
        flows.assert_login_success()

    @pytest.mark.regression
    @pytest.mark.boundary
    def test_invalid_credentials(self, flows: Flows, test_run_data: TestRunData) -> None:
        """Scenario 2 — wrong password surfaces the exact error string."""
        flows.perform_failed_login(username=cfg.STANDARD_USER, password=test_run_data.login.wrong_password)
        flows.assert_login_error(expected_error=test_run_data.login.invalid_credentials_error)
