from __future__ import annotations

from uuid import UUID

from apps.trucks.application.dtos.commands import CreateTruckCommand, TruckDto, UpdateTruckCommand
from apps.trucks.application.use_cases.create_truck_use_case import CreateTruckUseCase
from apps.trucks.application.use_cases.delete_truck_use_case import DeleteTruckUseCase
from apps.trucks.application.use_cases.list_trucks_use_case import ListTrucksUseCase
from apps.trucks.application.use_cases.update_truck_use_case import UpdateTruckUseCase


class TruckController:
    def __init__(
        self,
        *,
        list_trucks_use_case: ListTrucksUseCase,
        create_truck_use_case: CreateTruckUseCase,
        update_truck_use_case: UpdateTruckUseCase,
        delete_truck_use_case: DeleteTruckUseCase,
    ):
        self._list_trucks_use_case = list_trucks_use_case
        self._create_truck_use_case = create_truck_use_case
        self._update_truck_use_case = update_truck_use_case
        self._delete_truck_use_case = delete_truck_use_case

    def list_trucks(self) -> list[TruckDto]:
        return self._list_trucks_use_case.execute()

    def create_truck(self, command: CreateTruckCommand) -> TruckDto:
        return self._create_truck_use_case.execute(command)

    def update_truck(self, *, truck_id: UUID, command: UpdateTruckCommand) -> TruckDto:
        return self._update_truck_use_case.execute(truck_id=truck_id, command=command)

    def delete_truck(self, truck_id: UUID) -> None:
        self._delete_truck_use_case.execute(truck_id)
