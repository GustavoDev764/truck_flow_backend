from __future__ import annotations

from decimal import Decimal
from types import SimpleNamespace
from uuid import uuid4

from django.test import SimpleTestCase

from apps.trucks.application.dtos.commands import CreateTruckCommand, TruckDto, UpdateTruckCommand
from apps.trucks.application.services.truck_controller import TruckController


class TruckControllerSpec(SimpleTestCase):
    def test_controller_delegates_list_create_update(self):
        list_use_case = SimpleNamespace(
            execute=lambda: [
                TruckDto(
                    id=uuid4(),
                    license_plate="A",
                    brand="B",
                    model="C",
                    manufacturing_year=2020,
                    fipe_price=Decimal("1.00"),
                )
            ]
        )
        create_use_case = SimpleNamespace(
            execute=lambda cmd: TruckDto(
                id=uuid4(),
                license_plate=cmd.license_plate,
                brand=cmd.brand,
                model=cmd.model,
                manufacturing_year=cmd.manufacturing_year,
                fipe_price=Decimal("2.00"),
            )
        )
        update_use_case = SimpleNamespace(
            execute=lambda *, truck_id, command: TruckDto(
                id=truck_id,
                license_plate="X",
                brand=command.brand,
                model=command.model,
                manufacturing_year=command.manufacturing_year,
                fipe_price=Decimal("3.00"),
            )
        )

        controller = TruckController(
            list_trucks_use_case=list_use_case,
            create_truck_use_case=create_use_case,
            update_truck_use_case=update_use_case,
        )

        dtos = controller.list_trucks()
        self.assertEqual(len(dtos), 1)

        cmd = CreateTruckCommand(
            license_plate="ABC-1234", brand="Scania", model="FH 540", manufacturing_year=2020
        )
        created = controller.create_truck(cmd)
        self.assertEqual(created.license_plate, "ABC-1234")

        update_cmd = UpdateTruckCommand(brand="Volvo", model="FH 460", manufacturing_year=2019)
        truck_id = uuid4()
        updated = controller.update_truck(truck_id=truck_id, command=update_cmd)
        self.assertEqual(updated.id, truck_id)
        self.assertEqual(updated.brand, "Volvo")
