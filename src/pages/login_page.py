"""Login page — all selectors come from Swag Labs data-test attributes."""
from __future__ import annotations

import logging

from pages.base_page import BasePage

logger = logging.getLogger(__name__)


class LoginPage(BasePage):
    # ── Selectors (data-test where available) ─────────────────────────────
    _USERNAME_INPUT = "username"           # data-test="username"
    _PASSWORD_INPUT = "password"           # data-test="password"
    _LOGIN_BUTTON = "login-button"         # data-test="login-button"
    _ERROR_MESSAGE = "error"               # data-test on the error container

    # ── Actions ───────────────────────────────────────────────────────────

    def open(self) -> "LoginPage":
        self.goto("/")
        logger.info("Login page opened")
        return self

    def login(self, username: str, password: str) -> None:
        logger.info("Logging in as '%s'", username)
        self.get_by_test_id(self._USERNAME_INPUT).fill(username)
        self.get_by_test_id(self._PASSWORD_INPUT).fill(password)
        self.get_by_test_id(self._LOGIN_BUTTON).click()

    # ── Assertions / state queries ────────────────────────────────────────

    def error_message(self) -> str:
        """Return the visible error message text (raises if not present)."""
        container = self.get_by_test_id(self._ERROR_MESSAGE)
        container.wait_for(state="visible")
        text = container.text_content() or ""
        logger.debug("Error message text: %r", text)
        return text

    def is_error_visible(self) -> bool:
        return self.get_by_test_id(self._ERROR_MESSAGE).is_visible()
