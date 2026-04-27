"""Login test data."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class LoginData:
    # Intentionally wrong password used in the negative-path scenario.
    wrong_password: str = "wrong_password_xyz"

    # Exact error wording rendered by SauceDemo — test fails loudly if the app changes it.
    invalid_credentials_error: str = (
        "Epic sadface: Username and password do not match any user in this service"
    )


# ── Module-level constants (kept for backward compatibility) ───────────────
_defaults = LoginData()
WRONG_PASSWORD: str = _defaults.wrong_password
INVALID_CREDENTIALS_ERROR: str = _defaults.invalid_credentials_error
