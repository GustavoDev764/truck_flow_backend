from __future__ import annotations

from dataclasses import dataclass
from decimal import Decimal
from uuid import UUID

from apps.trucks.domain.entities import Truck
from apps.trucks.domain.exceptions import InvalidFipeDataError
from apps.trucks.domain.repositories import FipeClient, TruckRepository


@dataclass
class FipeCall:
    brand: str
    model: str
    manufacturing_year: int


class TruckRepositorySpy(TruckRepository):
    """
    Spy do repositório: guarda estado em memória e registra operações.
    """

    def __init__(self):
        self._by_id: dict[UUID, Truck] = {}
        self.saved: list[Truck] = []

    def get_by_id(self, truck_id: UUID) -> Truck | None:
        return self._by_id.get(truck_id)

    def get_by_license_plate(self, license_plate: str) -> Truck | None:
        for t in self._by_id.values():
            if t.license_plate == license_plate:
                return t
        return None

    def list(self) -> list[Truck]:
        return list(self._by_id.values())

    def save(self, truck: Truck) -> Truck:
        self._by_id[truck.id] = truck
        self.saved.append(truck)
        return truck


class FipeClientSpy(FipeClient):
    """
    Spy do client FIPE: retorna um preço fixo e registra chamadas.
    """

    def __init__(self, *, price: Decimal, should_fail: bool = False):
        self._price = price
        self._should_fail = should_fail
        self.calls: list[FipeCall] = []

    def get_fipe_price(self, *, brand: str, model: str, manufacturing_year: int) -> Decimal:
        self.calls.append(FipeCall(brand=brand, model=model, manufacturing_year=manufacturing_year))
        if self._should_fail:
            raise InvalidFipeDataError("Falha simulada na FIPE.")
        return self._price


class FipeClientGenericErrorSpy(FipeClient):
    """
    Spy que simula erro genérico para validar o wrap em InvalidFipeDataError.
    """

    def __init__(self, *, should_fail: bool = True):
        self._should_fail = should_fail
        self.calls: list[FipeCall] = []

    def get_fipe_price(self, *, brand: str, model: str, manufacturing_year: int) -> Decimal:
        self.calls.append(FipeCall(brand=brand, model=model, manufacturing_year=manufacturing_year))
        if self._should_fail:
            raise RuntimeError("Falha genérica simulada na FIPE.")
        return Decimal("0.00")
