from __future__ import annotations

import unittest.mock as mock
from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from django.db import IntegrityError
from django.test import SimpleTestCase

from apps.trucks.domain.entities import Truck
from apps.trucks.infrastructure.persistence.repositories import DjangoTruckRepository


class PersistenceRepositorySpec(SimpleTestCase):
    def test_get_by_id_and_get_by_license_plate(self):
        repo = DjangoTruckRepository()
        truck_id = uuid4()

        fake_obj = SimpleNamespace(
            id=truck_id,
            license_plate="ABC-1234",
            brand="Scania",
            model_name="FH 540",
            manufacturing_year=2020,
            fipe_price=Decimal("123.45"),
        )

        with mock.patch(
            "apps.trucks.infrastructure.persistence.repositories.TruckModel"
        ) as TruckModelMock:

            TruckModelMock.objects.get.return_value = fake_obj
            by_id = repo.get_by_id(truck_id)
            self.assertIsNotNone(by_id)
            self.assertEqual(by_id.id, truck_id)
            self.assertEqual(by_id.model, "FH 540")

            TruckModelMock.DoesNotExist = type("DoesNotExist", (Exception,), {})
            TruckModelMock.objects.get.side_effect = TruckModelMock.DoesNotExist()
            self.assertIsNone(repo.get_by_id(truck_id))

            TruckModelMock.objects.filter.return_value.first.return_value = fake_obj
            by_plate = repo.get_by_license_plate("ABC-1234")
            self.assertIsNotNone(by_plate)

            TruckModelMock.objects.filter.return_value.first.return_value = None
            self.assertIsNone(repo.get_by_license_plate("NOPE-0000"))

    def test_list_orders_by_created_at_desc(self):
        repo = DjangoTruckRepository()
        o2 = SimpleNamespace(
            id=uuid4(),
            license_plate="BBB-2222",
            brand="Volvo",
            model_name="FH 460",
            manufacturing_year=2019,
            fipe_price=Decimal("20.00"),
        )
        o1 = SimpleNamespace(
            id=uuid4(),
            license_plate="AAA-1111",
            brand="Scania",
            model_name="FH 540",
            manufacturing_year=2020,
            fipe_price=Decimal("10.00"),
        )

        with mock.patch(
            "apps.trucks.infrastructure.persistence.repositories.TruckModel"
        ) as TruckModelMock:
            TruckModelMock.objects.all.return_value.order_by.return_value = [o2, o1]
            trucks = repo.list()
            self.assertEqual(len(trucks), 2)
            self.assertEqual(trucks[0].license_plate, "BBB-2222")

    def test_save_upsert_by_id_updates(self):
        repo = DjangoTruckRepository()

        truck_id = uuid4()
        base = Truck(
            id=truck_id,
            license_plate="ABC-1234",
            brand="Scania",
            model="FH 540",
            manufacturing_year=2020,
            fipe_price=Decimal("100.00"),
        )

        fake_obj = SimpleNamespace(
            id=truck_id,
            license_plate="ABC-1234",
            brand="Scania",
            model_name="FH 540",
            manufacturing_year=2020,
            fipe_price=Decimal("100.00"),
        )

        with mock.patch(
            "apps.trucks.infrastructure.persistence.repositories.TruckModel"
        ) as TruckModelMock:
            TruckModelMock.objects.update_or_create.return_value = (fake_obj, True)

            saved_1 = DjangoTruckRepository.save.__wrapped__(repo, base)
            self.assertEqual(saved_1.id, truck_id)

    def test_save_raises_integrity_error_when_update_or_create_fails(self):
        repo = DjangoTruckRepository()

        truck_id = uuid4()
        base = Truck(
            id=truck_id,
            license_plate="ABC-1234",
            brand="Scania",
            model="FH 540",
            manufacturing_year=2020,
            fipe_price=Decimal("100.00"),
        )

        with mock.patch(
            "apps.trucks.infrastructure.persistence.repositories.TruckModel"
        ) as TruckModelMock:
            TruckModelMock.objects.update_or_create.side_effect = IntegrityError(
                "violação de integridade"
            )
            with self.assertRaises(IntegrityError):
                DjangoTruckRepository.save.__wrapped__(repo, base)
