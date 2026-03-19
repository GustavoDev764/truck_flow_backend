from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class Truck:
    id: UUID
    license_plate: str
    brand: str
    model: str
    manufacturing_year: int
    fipe_price: Decimal

    def with_updated_fipe(
        self,
        *,
        brand: str,
        model: str,
        manufacturing_year: int,
        fipe_price: Decimal,
    ) -> Truck:
        return Truck(
            id=self.id,
            license_plate=self.license_plate,
            brand=brand,
            model=model,
            manufacturing_year=manufacturing_year,
            fipe_price=fipe_price,
        )
