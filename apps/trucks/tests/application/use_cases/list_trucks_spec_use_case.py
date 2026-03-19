from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from django.test import SimpleTestCase

from apps.trucks.application.use_cases.list_trucks_use_case import ListTrucksUseCase
from apps.trucks.domain.entities import Truck
from apps.trucks.tests.application.mocks.truck_use_case_spy import TruckRepositorySpy


def makeSut(*, repo: TruckRepositorySpy | None = None):
    repo = repo or TruckRepositorySpy()
    return ListTrucksUseCase(truck_repo=repo), repo


class ListTrucksUseCaseSpec(SimpleTestCase):
    def test_returns_dtos(self):
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
        repo.save(
            Truck(
                id=uuid4(),
                license_plate="DEF-5678",
                brand="Scania",
                model="FH 540",
                manufacturing_year=2020,
                fipe_price=Decimal("2000.00"),
            )
        )

        use_case, _repo = makeSut(repo=repo)

        dtos = use_case.execute()
        self.assertEqual(len(dtos), 2)
