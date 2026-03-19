from __future__ import annotations

from decimal import Decimal
from typing import Protocol
from uuid import UUID

from .entities import Truck


class TruckRepository(Protocol):
    def get_by_id(self, truck_id: UUID) -> Truck | None: ...

    def get_by_license_plate(self, license_plate: str) -> Truck | None: ...

    def list(self) -> list[Truck]: ...

    def save(self, truck: Truck) -> Truck: ...

    def delete(self, truck_id: UUID) -> None: ...


class FipeClient(Protocol):
    def get_fipe_price(self, *, brand: str, model: str, manufacturing_year: int) -> Decimal: ...
