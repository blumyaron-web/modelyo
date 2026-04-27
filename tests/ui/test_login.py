"""
UI — Login tests
Scenario 1: Happy path  → lands on inventory page, items visible.
Scenario 2: Invalid creds → error message matches the exact app text.
"""
from __future__ import annotations

import pytest
from playwright.sync_api import Page

from config.config import cfg
from flows.login_flow import (
    assert_login_error,
    assert_login_success,
    perform_failed_login,
    perform_login,
)

pytestmark = [
    pytest.mark.ui,
    pytest.mark.playwright,
    pytest.mark.authentication,
    pytest.mark.smoke,
]

# The exact wording the app renders — test fails loudly if it changes.
EXPECTED_ERROR = "Epic sadface: Username and password do not match any user in this service"


class TestLogin:
    @pytest.mark.regression
    def test_happy_path(self, page: Page) -> None:
        """Scenario 1 — valid credentials land on a populated inventory page."""
        inventory = perform_login(page, username=cfg.STANDARD_USER, password=cfg.PASSWORD)
        assert_login_success(inventory)

    @pytest.mark.regression
    @pytest.mark.boundary
    def test_invalid_credentials(self, page: Page) -> None:
        """Scenario 2 — wrong password surfaces the exact error string."""
        login = perform_failed_login(page, username=cfg.STANDARD_USER, password="wrong_password_xyz")
        assert_login_error(login, expected_error=EXPECTED_ERROR)
