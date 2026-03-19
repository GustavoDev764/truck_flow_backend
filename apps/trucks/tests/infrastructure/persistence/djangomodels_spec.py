from __future__ import annotations

import uuid
from decimal import Decimal

from django.test import SimpleTestCase

from apps.trucks.infrastructure.persistence.django_models import TruckModel


class DjangoModelsSpec(SimpleTestCase):
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
