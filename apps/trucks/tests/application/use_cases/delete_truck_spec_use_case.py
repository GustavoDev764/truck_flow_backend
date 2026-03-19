from __future__ import annotations

from decimal import Decimal
from uuid import uuid4

from django.test import SimpleTestCase

from apps.trucks.application.use_cases.delete_truck_use_case import DeleteTruckUseCase
from apps.trucks.domain.entities import Truck
from apps.trucks.domain.exceptions import TruckNotFoundError
from apps.trucks.tests.application.mocks.truck_use_case_spy import TruckRepositorySpy


def make_sut(*, repo: TruckRepositorySpy | None = None) -> tuple[DeleteTruckUseCase, TruckRepositorySpy]:
    repo = repo or TruckRepositorySpy()
    return DeleteTruckUseCase(truck_repo=repo), repo


class DeleteTruckUseCaseSpec(SimpleTestCase):
    def test_deletes_existing_truck(self):
        truck_id = uuid4()
        truck = Truck(
            id=truck_id,
            license_plate="ABC-1234",
            brand="Scania",
            model="FH 540",
            manufacturing_year=2020,
            fipe_price=Decimal("100.00"),
        )
        repo = TruckRepositorySpy()
        repo._by_id[truck_id] = truck
        use_case, _ = make_sut(repo=repo)

        use_case.execute(truck_id)

        self.assertNotIn(truck_id, repo._by_id)

    def test_raises_truck_not_found_when_missing(self):
        repo = TruckRepositorySpy()
        use_case, _ = make_sut(repo=repo)
        truck_id = uuid4()

        with self.assertRaises(TruckNotFoundError):
            use_case.execute(truck_id)
