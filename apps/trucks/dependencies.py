from __future__ import annotations

from apps.trucks.application.dtos.commands import CreateTruckCommand, UpdateTruckCommand
from apps.trucks.application.services.truck_controller import TruckController
from apps.trucks.application.use_cases.create_truck_use_case import CreateTruckUseCase
from apps.trucks.application.use_cases.delete_truck_use_case import DeleteTruckUseCase
from apps.trucks.application.use_cases.list_trucks_use_case import ListTrucksUseCase
from apps.trucks.application.use_cases.update_truck_use_case import UpdateTruckUseCase
from apps.trucks.infrastructure.fipe.client import FipeClientHttp
from apps.trucks.infrastructure.persistence.repositories import DjangoTruckRepository


def make_controller_entity() -> TruckController:
    """
    Factory (composition root): monta o controller injetando use cases concretos.
    """

    return TruckController(
        list_trucks_use_case=build_list_trucks_use_case(),
        create_truck_use_case=build_create_truck_use_case(),
        update_truck_use_case=build_update_truck_use_case(),
        delete_truck_use_case=build_delete_truck_use_case(),
    )


def make_create_entity(payload: dict) -> CreateTruckCommand:
    """
    Factory de command para criação.
    Observação: a validação/normalização de payload deve ocorrer nos serializers.
    """

    return CreateTruckCommand(
        license_plate=payload["license_plate"],
        brand=payload["brand"],
        model=payload["model"],
        manufacturing_year=payload["manufacturing_year"],
    )


def make_update_entity(payload: dict) -> UpdateTruckCommand:
    return UpdateTruckCommand(
        brand=payload["brand"],
        model=payload["model"],
        manufacturing_year=payload["manufacturing_year"],
    )


def build_create_truck_use_case() -> CreateTruckUseCase:
    return CreateTruckUseCase(truck_repo=DjangoTruckRepository(), fipe_client=FipeClientHttp())


def build_list_trucks_use_case() -> ListTrucksUseCase:
    return ListTrucksUseCase(truck_repo=DjangoTruckRepository())


def build_update_truck_use_case() -> UpdateTruckUseCase:
    return UpdateTruckUseCase(truck_repo=DjangoTruckRepository(), fipe_client=FipeClientHttp())


def build_delete_truck_use_case() -> DeleteTruckUseCase:
    return DeleteTruckUseCase(truck_repo=DjangoTruckRepository())
