from __future__ import annotations

from decimal import ROUND_HALF_UP, Decimal


def quantize_money(value: Decimal) -> Decimal:
    return value.quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)
