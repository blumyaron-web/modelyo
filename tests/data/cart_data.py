"""Cart test data."""
from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class CartData:
    # Scenario 3: two distinct products used to verify badge count and cart contents.
    products: tuple[str, ...] = (
        "Sauce Labs Backpack",
        "Sauce Labs Bike Light",
    )

    # Bonus B2: three products used to exercise badge increment / decrement cycle.
    badge_cycle_products: tuple[str, ...] = (
        "Sauce Labs Backpack",
        "Sauce Labs Bike Light",
        "Sauce Labs Onesie",
    )


# ── Module-level constants (kept for backward compatibility) ───────────────
_defaults = CartData()
CART_PRODUCTS: list[str] = list(_defaults.products)
BADGE_CYCLE_PRODUCTS: list[str] = list(_defaults.badge_cycle_products)
