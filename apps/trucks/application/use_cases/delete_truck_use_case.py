from __future__ import annotations

from uuid import UUID

from apps.trucks.domain.exceptions import TruckNotFoundError
from apps.trucks.domain.repositories import TruckRepository


class DeleteTruckUseCase:
    def __init__(self, truck_repo: TruckRepository):
        self._repo = truck_repo

    def execute(self, truck_id: UUID) -> None:
        truck = self._repo.get_by_id(truck_id)
        if truck is None:
            raise TruckNotFoundError(truck_id)
        self._repo.delete(truck_id)
