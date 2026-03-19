from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from apps.trucks.application.constants.money import quantize_money
from apps.trucks.application.dtos.commands import CreateTruckCommand, TruckDto
from apps.trucks.domain.entities import Truck
from apps.trucks.domain.exceptions import DuplicateLicensePlateError, InvalidFipeDataError
from apps.trucks.domain.repositories import FipeClient, TruckRepository


class CreateTruckUseCase:
    def __init__(self, *, truck_repo: TruckRepository, fipe_client: FipeClient):
        self._truck_repo = truck_repo
        self._fipe_client = fipe_client

    def execute(self, command: CreateTruckCommand) -> TruckDto:
        existing = self._truck_repo.get_by_license_plate(command.license_plate)
        if existing is not None:
            raise DuplicateLicensePlateError(command.license_plate)

        try:
            fipe_price: Decimal = self._fipe_client.get_fipe_price(
                brand=command.brand,
                model=command.model,
                manufacturing_year=command.manufacturing_year,
            )
        except InvalidFipeDataError:
            raise
        except Exception as exc:
            raise InvalidFipeDataError(str(exc)) from exc

        truck = Truck(
            id=uuid4(),
            license_plate=command.license_plate,
            brand=command.brand,
            model=command.model,
            manufacturing_year=command.manufacturing_year,
            fipe_price=quantize_money(fipe_price),
        )
        saved = self._truck_repo.save(truck)

        return TruckDto(
            id=saved.id,
            license_plate=saved.license_plate,
            brand=saved.brand,
            model=saved.model,
            manufacturing_year=saved.manufacturing_year,
            fipe_price=saved.fipe_price,
        )
