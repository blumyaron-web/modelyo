"""API-layer fixtures.

Defines the ``flows`` fixture for API tests.  The fixture receives a fresh
:class:`~clients.api_client.APIClient` instance; no browser is started.
"""
from __future__ import annotations

import pytest

from clients.api_client import APIClient
from flows.flows import Flows


@pytest.fixture()
def flows(api_client: APIClient) -> Flows:
    """Return a :class:`Flows` instance backed by an HTTP API client."""
    return Flows(api_client=api_client)
