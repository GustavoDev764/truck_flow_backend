from __future__ import annotations

import uuid
from decimal import Decimal

from django.test import TestCase

from apps.trucks.infrastructure.persistence.django_models import TruckModel


class DjangoModelsSpec(TestCase):
    def test_save_generates_uuid_when_id_missing(self):
        """UUIDModel usa id como UUID (default=uuid.uuid4)."""
        obj = TruckModel(
            license_plate="XYZ-9999",
            brand="Scania",
            model_name="FH 540",
            manufacturing_year=2020,
            fipe_price=Decimal("1.00"),
        )

        obj.save()
        self.assertIsNotNone(obj.id)
        self.assertIsInstance(obj.id, uuid.UUID)

    def test_model_property_returns_model_name(self):
        obj = TruckModel(
            id=uuid.uuid4(),
            license_plate="ABC-1234",
            brand="Scania",
            model_name="FH 540",
            manufacturing_year=2020,
            fipe_price=Decimal("1.00"),
        )
        self.assertEqual(obj.model, "FH 540")
