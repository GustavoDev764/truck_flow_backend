from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from django.test import SimpleTestCase

from apps.trucks.application.dtos.commands import CreateTruckCommand
from apps.trucks.application.use_cases.create_truck_use_case import CreateTruckUseCase
from apps.trucks.domain.entities import Truck
from apps.trucks.domain.exceptions import DuplicateLicensePlateError, InvalidFipeDataError
from apps.trucks.tests.application.mocks.truck_use_case_spy import (
    FipeClientGenericErrorSpy,
    FipeClientSpy,
    TruckRepositorySpy,
)


def makeSut(*, repo: TruckRepositorySpy | None = None, fipe: FipeClientSpy | None = None):
    repo = repo or TruckRepositorySpy()
    fipe = fipe or FipeClientSpy(price=Decimal("0"))
    return CreateTruckUseCase(truck_repo=repo, fipe_client=fipe), repo, fipe


class CreateTruckUseCaseSpec(SimpleTestCase):
    def test_success_sets_fipe_price(self):
        use_case, _repo, fipe = makeSut(fipe=FipeClientSpy(price=Decimal("123.1")))
        command = CreateTruckCommand(
            license_plate="ABC-1234",
            brand="Scania",
            model="FH 540",
            manufacturing_year=2020,
        )

        dto = use_case.execute(command)

        self.assertEqual(dto.license_plate, "ABC-1234")
        self.assertEqual(dto.brand, "Scania")
        self.assertEqual(dto.model, "FH 540")
        self.assertEqual(dto.manufacturing_year, 2020)
        self.assertEqual(dto.fipe_price, Decimal("123.10"))
        self.assertEqual(len(fipe.calls), 1)

    def test_duplicate_license_plate_raises(self):
        repo = TruckRepositorySpy()
        repo.save(
            Truck(
                id=uuid4(),
                license_plate="ABC-1234",
                brand="Volvo",
                model="R 450",
                manufacturing_year=2019,
                fipe_price=Decimal("1000.00"),
            )
        )
        use_case, _repo, _fipe = makeSut(repo=repo, fipe=FipeClientSpy(price=Decimal("999.99")))

        command = CreateTruckCommand(
            license_plate="ABC-1234",
            brand="Scania",
            model="FH 540",
            manufacturing_year=2020,
        )

        with self.assertRaises(DuplicateLicensePlateError):
            use_case.execute(command)

    def test_generic_exception_is_wrapped(self):
        repo = TruckRepositorySpy()
        use_case, _repo, _fipe = makeSut(repo=repo, fipe=FipeClientGenericErrorSpy())

        command = CreateTruckCommand(
            license_plate="XYZ-0001",
            brand="Scania",
            model="FH 540",
            manufacturing_year=2020,
        )

        with self.assertRaises(InvalidFipeDataError) as ctx:
            use_case.execute(command)

        self.assertIn("Falha genérica simulada na FIPE.", str(ctx.exception))

    def test_generic_error_spy_returns_when_should_fail_false(self):
        fipe = FipeClientGenericErrorSpy(should_fail=False)
        price = fipe.get_fipe_price(brand="X", model="Y", manufacturing_year=2020)
        self.assertEqual(price, Decimal("0.00"))
        self.assertEqual(len(fipe.calls), 1)

    def test_invalid_fipe_data_is_reraised(self):
        repo = TruckRepositorySpy()
        fipe = FipeClientSpy(price=Decimal("0"), should_fail=True)
        use_case, _repo, _fipe = makeSut(repo=repo, fipe=fipe)

        command = CreateTruckCommand(
            license_plate="XYZ-0003",
            brand="Scania",
            model="FH 540",
            manufacturing_year=2020,
        )

        with self.assertRaises(InvalidFipeDataError):
            use_case.execute(command)
