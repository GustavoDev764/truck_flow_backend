from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID


@dataclass(frozen=True, slots=True)
class CreateTruckCommand:
    license_plate: str
    brand: str
    model: str
    manufacturing_year: int


@dataclass(frozen=True, slots=True)
class UpdateTruckCommand:
    brand: str
    model: str
    manufacturing_year: int


@dataclass(frozen=True, slots=True)
class TruckDto:
    id: UUID
    license_plate: str
    brand: str
    model: str
    manufacturing_year: int
    fipe_price: Decimal
