"""TestRunData — single fixture-injectable data object for all test domains.

Tests receive this via the ``test_run_data`` pytest fixture and access data
through domain namespaces:

    test_run_data.checkout.product
    test_run_data.checkout.first_name
    test_run_data.cart.products
    test_run_data.posts.create_payload
    ...

Each domain attribute is itself a frozen dataclass, so all leaf values are
immutable and carry full type information.
"""
from __future__ import annotations

from dataclasses import dataclass, field

from tests.data.cart_data import CartData
from tests.data.checkout_data import CheckoutData
from tests.data.login_data import LoginData
from tests.data.posts_data import PostsData
from tests.data.sort_data import SortData


@dataclass(frozen=True)
class TestRunData:
    """Aggregated test-data object injected into tests via the ``test_run_data`` fixture.

    Attributes:
        login:    Credentials and expected error strings.
        cart:     Product lists for cart and badge scenarios.
        checkout: Shopper info, product, and confirmation header.
        sort:     Sort option keys.
        posts:    Post IDs and CRUD payloads.
    """

    login: LoginData = field(default_factory=LoginData)
    cart: CartData = field(default_factory=CartData)
    checkout: CheckoutData = field(default_factory=CheckoutData)
    sort: SortData = field(default_factory=SortData)
    posts: PostsData = field(default_factory=PostsData)
