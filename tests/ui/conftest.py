"""UI-layer fixtures.

Defines the ``flows`` fixture for UI tests.  The fixture receives a page
that is already authenticated (via ``logged_in_page``) so individual tests
never have to repeat login steps.

Tests that need an unauthenticated page should use the ``flows_unauthenticated``
fixture defined in ``tests/fixtures/flows.py``.
"""
from __future__ import annotations

import pytest
from playwright.sync_api import Page

from flows.flows import Flows


@pytest.fixture()
def flows(logged_in_page: Page) -> Flows:
    """Return a :class:`Flows` instance backed by an already-logged-in page."""
    return Flows(page=logged_in_page)
