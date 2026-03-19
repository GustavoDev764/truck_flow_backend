from __future__ import annotations

from apps.trucks.application.dtos.commands import TruckDto
from apps.trucks.domain.repositories import TruckRepository


class ListTrucksUseCase:
    def __init__(self, *, truck_repo: TruckRepository):
        self._truck_repo = truck_repo

    def execute(self) -> list[TruckDto]:
        trucks = self._truck_repo.list()
        return [
            TruckDto(
                id=t.id,
                license_plate=t.license_plate,
                brand=t.brand,
                model=t.model,
                manufacturing_year=t.manufacturing_year,
                fipe_price=t.fipe_price,
            )
            for t in trucks
        ]
