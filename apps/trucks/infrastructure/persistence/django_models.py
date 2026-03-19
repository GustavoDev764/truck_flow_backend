from __future__ import annotations

from django.db import models

from core.models import UUIDModel


class TruckModel(UUIDModel):
    license_plate = models.CharField(max_length=16, unique=True)
    brand = models.CharField(max_length=255)
    model_name = models.CharField(max_length=255)
    manufacturing_year = models.PositiveIntegerField()
    fipe_price = models.DecimalField(max_digits=12, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def model(self) -> str:
        return self.model_name
