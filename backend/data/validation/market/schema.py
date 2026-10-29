from __future__ import annotations

from dataclasses import dataclass
from datetime import date


@dataclass(frozen=True)
class MarketObservation:
    """
    Normalized historical market observation used for validation.

    `value` is a level/index/spot price, not a return.
    """

    date: date
    asset: str
    value: float
    source: str
    value_type: str