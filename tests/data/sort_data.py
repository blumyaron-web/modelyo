"""Sort test data."""
from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SortData:
    # Sort option key accepted by the inventory dropdown.
    # Matches the ``value`` attribute of the ``<option>`` element on SauceDemo.
    #   'az'   — Name (A to Z)
    #   'za'   — Name (Z to A)
    #   'lohi' — Price (low to high)
    #   'hilo' — Price (high to low)
    price_low_to_high: str = "lohi"


# ── Module-level constants (kept for backward compatibility) ───────────────
_defaults = SortData()
PRICE_LOW_TO_HIGH: str = _defaults.price_low_to_high
