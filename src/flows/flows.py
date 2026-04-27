"""Flows façade — single injectable entry point for all test flows.

Injected into tests via the ``flows`` pytest fixture defined in each layer's
``conftest.py``.  Tests never import page objects or individual flow modules
directly; all interactions go through this class.

UI tests (``tests/ui/conftest.py``)::

    @pytest.fixture()
    def flows(logged_in_page: Page) -> Flows:
        return Flows(page=logged_in_page)

API tests (``tests/api/conftest.py``)::

    @pytest.fixture()
    def flows(api_client: APIClient) -> Flows:
        return Flows(api_client=api_client)

Login tests override the fixture locally to receive an unauthenticated page::

    @pytest.fixture()
    def flows(page: Page) -> Flows:
        return Flows(page=page)
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from playwright.sync_api import Page

    from clients.api_client import APIClient

from flows import api_flow, cart_flow, checkout_flow, login_flow, sort_flow
from pages.cart_page import CartPage
from pages.inventory_page import InventoryPage

logger = logging.getLogger(__name__)


class Flows:
    """Aggregated test-flow façade.

    Args:
        page:       Playwright ``Page`` — authenticated or not depending on which
                    fixture provides it.  Required for all UI flow methods.
        api_client: HTTP client.  Required for all API flow methods.

    Intermediate results (e.g. the cart page, checkout header, price list) are
    stored as private attributes so that chained assertion methods can access
    them without the test having to juggle return values.
    """

    def __init__(
        self,
        *,
        page: "Page | None" = None,
        api_client: "APIClient | None" = None,
    ) -> None:
        self._page = page
        self._client = api_client

        # Intermediate state set by action methods and consumed by assertions
        self._login_result: Any = None   # InventoryPage | LoginPage
        self._cart: CartPage | None = None
        self._checkout_header: str | None = None
        self._prices: list[float] | None = None

    # ── Internal helpers ──────────────────────────────────────────────────

    @property
    def _inventory(self) -> InventoryPage:
        assert self._page is not None, "Flows.page is required for UI operations"
        return InventoryPage(self._page)

    # ── Login flow ────────────────────────────────────────────────────────

    def perform_login(self, username: str, password: str) -> None:
        """Navigate to login page, submit valid credentials, wait for inventory."""
        self._login_result = login_flow.perform_login(self._page, username, password)

    def perform_failed_login(self, username: str, password: str) -> None:
        """Submit credentials that are expected to fail; stay on the login page."""
        self._login_result = login_flow.perform_failed_login(self._page, username, password)

    def assert_login_success(self) -> None:
        """Soft-assert the inventory is visible and contains items after login."""
        login_flow.assert_login_success(self._login_result)

    def assert_login_error(self, expected_error: str) -> None:
        """Soft-assert the login page shows the exact expected error string."""
        login_flow.assert_login_error(self._login_result, expected_error=expected_error)

    # ── Cart flow ─────────────────────────────────────────────────────────

    def add_items_to_cart(self, products: list[str]) -> None:
        """Click *Add to cart* for every product name in *products*."""
        cart_flow.add_items_to_cart(self._inventory, products)

    def open_cart(self) -> CartPage:
        """Click the cart icon and wait for the cart page; stores result internally."""
        self._cart = cart_flow.open_cart(self._page, self._inventory)
        return self._cart

    def assert_cart_badge(self, expected_count: int) -> None:
        """Soft-assert the cart badge shows *expected_count*."""
        cart_flow.assert_cart_badge(self._inventory, expected_count=expected_count)

    def assert_cart_contents(self, expected_products: list[str]) -> None:
        """Soft-assert every product appears in the cart with a valid price."""
        assert self._cart is not None, "Call open_cart() before assert_cart_contents()"
        cart_flow.assert_cart_contents(self._cart, expected_products=expected_products)

    def assert_badge_increments(self, products: list[str]) -> None:
        """Add products one-by-one and soft-assert the badge increments each time."""
        cart_flow.assert_badge_increments(self._inventory, products)

    def assert_badge_decrements(self, products: list[str]) -> None:
        """Remove products one-by-one and soft-assert the badge decrements each time."""
        cart_flow.assert_badge_decrements(self._inventory, products)

    # ── Checkout flow ─────────────────────────────────────────────────────

    def complete_checkout(
        self,
        *,
        first_name: str,
        last_name: str,
        postal_code: str,
    ) -> None:
        """Drive the full checkout sequence; stores confirmation header internally."""
        self._checkout_header = checkout_flow.complete_checkout(
            self._page,
            first_name=first_name,
            last_name=last_name,
            postal_code=postal_code,
        )

    def assert_order_confirmed(self, expected_header: str) -> None:
        """Soft-assert the order-confirmation header matches *expected_header*."""
        assert self._checkout_header is not None, "Call complete_checkout() first"
        checkout_flow.assert_order_confirmed(
            self._checkout_header, expected_header=expected_header
        )

    # ── Sort flow ─────────────────────────────────────────────────────────

    def sort_and_get_prices(self, sort_value: str) -> None:
        """Apply a sort option and store all visible prices internally."""
        self._prices = sort_flow.sort_and_get_prices(
            self._page, self._inventory, sort_value
        )

    def assert_prices_ascending(self) -> None:
        """Soft-assert the stored price list is non-empty and in ascending order."""
        assert self._prices is not None, "Call sort_and_get_prices() first"
        sort_flow.assert_prices_ascending(self._prices)

    # ── API flow ──────────────────────────────────────────────────────────

    def assert_get_all_posts(self) -> None:
        """GET /posts → soft-assert 200, 100-item array, and schema correctness."""
        assert self._client is not None, "Flows.api_client is required for API operations"
        response = self._client.get("/posts")
        api_flow.assert_get_all_posts(response)

    def assert_get_single_post(self, post_id: int) -> None:
        """GET /posts/{id} → soft-assert 200 with the expected id."""
        assert self._client is not None, "Flows.api_client is required for API operations"
        response = self._client.get(f"/posts/{post_id}")
        api_flow.assert_get_single_post(response, expected_id=post_id)

    def assert_not_found(self, post_id: int) -> None:
        """GET /posts/{id} → soft-assert 404 for a non-existent resource."""
        assert self._client is not None, "Flows.api_client is required for API operations"
        response = self._client.get(f"/posts/{post_id}")
        api_flow.assert_not_found(response, post_id=post_id)

    def assert_create_post(self, payload: dict) -> None:
        """POST /posts → soft-assert 201 with echoed payload and generated id."""
        assert self._client is not None, "Flows.api_client is required for API operations"
        response = self._client.post("/posts", json=payload)
        api_flow.assert_create_post(response, payload=payload)

    def assert_update_post(self, payload: dict, target_id: int) -> None:
        """PUT /posts/{id} → soft-assert 200 with the updated fields."""
        assert self._client is not None, "Flows.api_client is required for API operations"
        response = self._client.put(f"/posts/{target_id}", json=payload)
        api_flow.assert_update_post(response, payload=payload, target_id=target_id)

    def assert_delete_post(self, post_id: int) -> None:
        """DELETE /posts/{id} → soft-assert 200 or 204."""
        assert self._client is not None, "Flows.api_client is required for API operations"
        response = self._client.delete(f"/posts/{post_id}")
        api_flow.assert_delete_post(response)
