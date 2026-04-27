"""
fixtures/flows.py — reusable Flows fixture variants.

Variants
--------
flows_unauthenticated
    A :class:`~flows.flows.Flows` instance backed by a *fresh, unauthenticated*
    page.  Use this in tests that drive the login flow themselves (e.g. login
    tests, logout tests).  Import via the ``flows_unauthenticated`` fixture name.
"""
from __future__ import annotations

import pytest
from playwright.sync_api import Page

from flows.flows import Flows


@pytest.fixture()
def flows_unauthenticated(page: Page) -> Flows:
    """Flows backed by a fresh, unauthenticated page."""
    return Flows(page=page)
