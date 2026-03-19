from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from django.test import SimpleTestCase

from apps.trucks.application.dtos.commands import UpdateTruckCommand
from apps.trucks.application.use_cases.update_truck_use_case import UpdateTruckUseCase
from apps.trucks.domain.entities import Truck
from apps.trucks.domain.exceptions import InvalidFipeDataError, TruckNotFoundError
from apps.trucks.tests.application.mocks.truck_use_case_spy import (
    FipeClientGenericErrorSpy,
    FipeClientSpy,
    TruckRepositorySpy,
)


def makeSut(*, repo: TruckRepositorySpy | None = None, fipe: FipeClientSpy | None = None):
    repo = repo or TruckRepositorySpy()
    fipe = fipe or FipeClientSpy(price=Decimal("0"))
    return UpdateTruckUseCase(truck_repo=repo, fipe_client=fipe), repo, fipe


class UpdateTruckUseCaseSpec(SimpleTestCase):
    def test_success_recalculates_fipe_price(self):
        repo = TruckRepositorySpy()
        truck_id = uuid4()
        repo.save(
            Truck(
                id=truck_id,
                license_plate="ABC-1234",
                brand="Volvo",
                model="R 450",
                manufacturing_year=2019,
                fipe_price=Decimal("1000.00"),
            )
        )

        use_case, _repo, fipe = makeSut(repo=repo, fipe=FipeClientSpy(price=Decimal("55")))

        command = UpdateTruckCommand(brand="Scania", model="FH 540", manufacturing_year=2020)
        dto = use_case.execute(truck_id=truck_id, command=command)

        self.assertEqual(dto.id, truck_id)
        self.assertEqual(dto.brand, "Scania")
        self.assertEqual(dto.model, "FH 540")
        self.assertEqual(dto.manufacturing_year, 2020)
        self.assertEqual(dto.fipe_price, Decimal("55.00"))
        self.assertEqual(len(fipe.calls), 1)

    def test_not_found_raises(self):
        repo = TruckRepositorySpy()
        use_case, _repo, _ = makeSut(repo=repo, fipe=FipeClientSpy(price=Decimal("55")))

        command = UpdateTruckCommand(brand="Scania", model="FH 540", manufacturing_year=2020)
        with self.assertRaises(TruckNotFoundError):
            use_case.execute(truck_id=uuid4(), command=command)

    def test_invalid_fipe_propagates(self):
        repo = TruckRepositorySpy()
        truck_id = uuid4()
        repo.save(
            Truck(
                id=truck_id,
                license_plate="ABC-1234",
                brand="Volvo",
                model="R 450",
                manufacturing_year=2019,
                fipe_price=Decimal("1000.00"),
            )
        )

        use_case, _repo, _ = makeSut(
            repo=repo, fipe=FipeClientSpy(price=Decimal("55"), should_fail=True)
        )
        command = UpdateTruckCommand(brand="Scania", model="FH 540", manufacturing_year=2020)
        with self.assertRaises(InvalidFipeDataError):
            use_case.execute(truck_id=truck_id, command=command)

    def test_generic_exception_is_wrapped(self):
        repo = TruckRepositorySpy()
        truck_id = uuid4()
        repo.save(
            Truck(
                id=truck_id,
                license_plate="ABC-1234",
                brand="Volvo",
                model="R 450",
                manufacturing_year=2019,
                fipe_price=Decimal("1000.00"),
            )
        )
        use_case, _repo, _ = makeSut(repo=repo, fipe=FipeClientGenericErrorSpy())

        command = UpdateTruckCommand(brand="Scania", model="FH 540", manufacturing_year=2020)
        with self.assertRaises(InvalidFipeDataError) as ctx:
            use_case.execute(truck_id=truck_id, command=command)

        self.assertIn("Falha genérica simulada na FIPE.", str(ctx.exception))
