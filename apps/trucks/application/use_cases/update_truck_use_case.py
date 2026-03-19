from __future__ import annotations

from uuid import UUID

from apps.trucks.application.constants.money import quantize_money
from apps.trucks.application.dtos.commands import TruckDto, UpdateTruckCommand
from apps.trucks.domain.exceptions import InvalidFipeDataError, TruckNotFoundError
from apps.trucks.domain.repositories import FipeClient, TruckRepository


class UpdateTruckUseCase:
    def __init__(self, *, truck_repo: TruckRepository, fipe_client: FipeClient):
        self._truck_repo = truck_repo
        self._fipe_client = fipe_client

    def execute(self, *, truck_id: UUID, command: UpdateTruckCommand) -> TruckDto:
        existing = self._truck_repo.get_by_id(truck_id)
        if existing is None:
            raise TruckNotFoundError(truck_id)

        try:
            fipe_price = self._fipe_client.get_fipe_price(
                brand=command.brand,
                model=command.model,
                manufacturing_year=command.manufacturing_year,
            )
        except InvalidFipeDataError:
            raise
        except Exception as exc:
            raise InvalidFipeDataError(str(exc)) from exc

        updated = existing.with_updated_fipe(
            brand=command.brand,
            model=command.model,
            manufacturing_year=command.manufacturing_year,
            fipe_price=quantize_money(fipe_price),
        )
        saved = self._truck_repo.save(updated)

        return TruckDto(
            id=saved.id,
            license_plate=saved.license_plate,
            brand=saved.brand,
            model=saved.model,
            manufacturing_year=saved.manufacturing_year,
            fipe_price=saved.fipe_price,
        )
