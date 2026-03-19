from __future__ import annotations

from uuid import UUID

from django.db import IntegrityError, transaction

from apps.trucks.domain.entities import Truck
from apps.trucks.domain.repositories import TruckRepository

from .django_models import TruckModel


class DjangoTruckRepository(TruckRepository):
    def get_by_id(self, truck_id: UUID) -> Truck | None:
        try:
            obj = TruckModel.objects.get(id=truck_id)
        except TruckModel.DoesNotExist:
            return None

        return self._to_domain(obj)

    def get_by_license_plate(self, license_plate: str) -> Truck | None:
        obj = TruckModel.objects.filter(license_plate=license_plate).first()
        if obj is None:
            return None
        return self._to_domain(obj)

    def list(self) -> list[Truck]:
        qs = TruckModel.objects.all().order_by("-created_at")
        return [self._to_domain(obj) for obj in qs]

    @transaction.atomic
    def save(self, truck: Truck) -> Truck:

        defaults = {
            "license_plate": truck.license_plate,
            "brand": truck.brand,
            "model_name": truck.model,
            "manufacturing_year": truck.manufacturing_year,
            "fipe_price": truck.fipe_price,
        }

        try:
            obj, _created = TruckModel.objects.update_or_create(id=truck.id, defaults=defaults)
        except IntegrityError as exc:

            raise exc

        return self._to_domain(obj)

    def delete(self, truck_id: UUID) -> None:
        TruckModel.objects.filter(id=truck_id).delete()

    def _to_domain(self, obj: TruckModel) -> Truck:
        return Truck(
            id=obj.id,
            license_plate=obj.license_plate,
            brand=obj.brand,
            model=obj.model_name,
            manufacturing_year=obj.manufacturing_year,
            fipe_price=obj.fipe_price,
        )
