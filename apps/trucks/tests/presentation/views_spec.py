from __future__ import annotations

from decimal import Decimal
from uuid import UUID, uuid4

from django.contrib.auth.models import Group, User
from django.test import TestCase
from rest_framework.request import Request as DRFRequest
from rest_framework.test import APIClient, APIRequestFactory

from apps.trucks.application.dtos.commands import CreateTruckCommand, TruckDto, UpdateTruckCommand
from apps.trucks.domain.exceptions import (
    DuplicateLicensePlateError,
    InvalidFipeDataError,
    TruckNotFoundError,
)
from apps.trucks.presentation.error_responses import TruckErrorResponseFactory
from apps.trucks.presentation.exception_handler import truck_exception_handler
from apps.trucks.presentation.response_factory import TruckResponseFactory
from apps.trucks.presentation.serializers import TruckCreateSerializer, TruckUpdateSerializer
from apps.trucks.presentation.views import TruckListCreateAPIView


class _FakeController:
    def __init__(self, *, list_dtos: list[TruckDto]):
        self._list_dtos = list_dtos
        self.created_commands: list[CreateTruckCommand] = []
        self.updated_calls: list[tuple[UUID, UpdateTruckCommand]] = []

    def list_trucks(self) -> list[TruckDto]:
        return self._list_dtos

    def create_truck(self, command: CreateTruckCommand) -> TruckDto:
        self.created_commands.append(command)
        return TruckDto(
            id=uuid4(),
            license_plate=command.license_plate,
            brand=command.brand,
            model=command.model,
            manufacturing_year=command.manufacturing_year,
            fipe_price=Decimal("123.45"),
        )

    def update_truck(self, *, truck_id, command: UpdateTruckCommand) -> TruckDto:
        self.updated_calls.append((truck_id, command))
        return TruckDto(
            id=truck_id,
            license_plate="ABC-0000",
            brand=command.brand,
            model=command.model,
            manufacturing_year=command.manufacturing_year,
            fipe_price=Decimal("55.00"),
        )

    def delete_truck(self, truck_id: UUID) -> None:
        pass


class PresentationViewsSpec(TestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.factory = APIRequestFactory()
        grp, _ = Group.objects.get_or_create(name="cliente")
        self.test_user = User.objects.create_user(username="test_cliente", password="test123")
        self.test_user.groups.add(grp)
        self.client.force_authenticate(user=self.test_user)

    def makeSut(
        self,
        *,
        list_dtos: list[TruckDto] | None = None,
        controller_override: _FakeController | None = None,
    ) -> _FakeController:
        if controller_override is not None:
            fake_controller = controller_override
        else:
            list_dtos = list_dtos or []
            fake_controller = _FakeController(list_dtos=list_dtos)

        import apps.trucks.presentation.views as views_module

        views_module._controller = fake_controller
        return fake_controller

    def test_serializers_validation_license_plate_empty(self):
        serializer = TruckCreateSerializer(
            data={
                "license_plate": "   ",
                "brand": "Scania",
                "model": "FH 540",
                "manufacturing_year": 2020,
            }
        )
        self.assertFalse(serializer.is_valid())

    def test_serializers_validation_manufacturing_year_out_of_range_create(self):
        serializer = TruckCreateSerializer(
            data={
                "license_plate": "ABC-1234",
                "brand": "Scania",
                "model": "FH 540",
                "manufacturing_year": 1899,
            }
        )
        self.assertFalse(serializer.is_valid())

    def test_serializers_validation_manufacturing_year_out_of_range_update(self):
        serializer = TruckUpdateSerializer(
            data={"brand": "Scania", "model": "FH 540", "manufacturing_year": 1899}
        )
        self.assertFalse(serializer.is_valid())

    def test_response_factory_success(self):
        dto = TruckDto(
            id=uuid4(),
            license_plate="ABC-1234",
            brand="Scania",
            model="FH 540",
            manufacturing_year=2020,
            fipe_price=Decimal("123.10"),
        )
        factory = TruckResponseFactory()

        list_response = factory.list_trucks([dto])
        self.assertEqual(list_response.status_code, 200)

        create_response = factory.create_truck(dto)
        self.assertEqual(create_response.status_code, 201)

        update_response = factory.update_truck(dto)
        self.assertEqual(update_response.status_code, 200)

    def test_exception_handler_maps_domain_errors(self):
        exc_list = [
            DuplicateLicensePlateError("ABC-1234"),
            InvalidFipeDataError("FIPE inválida"),
            TruckNotFoundError(uuid4()),
        ]

        for exc in exc_list:
            resp = truck_exception_handler(exc, context={})
            self.assertIsNotNone(resp)

        self.assertEqual(
            truck_exception_handler(DuplicateLicensePlateError("ABC-1234"), context={}).status_code,
            409,
        )
        self.assertEqual(
            truck_exception_handler(InvalidFipeDataError("FIPE inválida"), context={}).status_code,
            400,
        )
        self.assertEqual(
            truck_exception_handler(TruckNotFoundError(uuid4()), context={}).status_code, 404
        )

    def test_error_response_factory(self):
        factory = TruckErrorResponseFactory()
        self.assertEqual(factory.make(DuplicateLicensePlateError("ABC-1234")).status_code, 409)
        self.assertEqual(factory.make(InvalidFipeDataError("FIPE inválida")).status_code, 400)
        self.assertEqual(factory.make(TruckNotFoundError(uuid4())).status_code, 404)

    def test_views_list_pagination_page_1_defaults_10(self):
        dtos = [
            TruckDto(
                id=uuid4(),
                license_plate=f"PLACA-{i}",
                brand="Scania",
                model="FH 540",
                manufacturing_year=2020,
                fipe_price=Decimal("10.00"),
            )
            for i in range(15)
        ]

        self.makeSut(list_dtos=dtos)

        raw_request = self.factory.get("/api/trucks/", data={"page": 1})
        raw_request.user = self.test_user
        request = DRFRequest(raw_request)
        response = TruckListCreateAPIView().get(request)
        self.assertEqual(response.status_code, 200)
        self.assertIn("results", response.data)
        self.assertEqual(len(response.data["results"]), 10)

    def test_views_list_pagination_page_2(self):
        dtos = [
            TruckDto(
                id=uuid4(),
                license_plate=f"PLACA-{i}",
                brand="Scania",
                model="FH 540",
                manufacturing_year=2020,
                fipe_price=Decimal("10.00"),
            )
            for i in range(15)
        ]

        self.makeSut(list_dtos=dtos)

        raw_request = self.factory.get("/api/trucks/", data={"page": 2})
        raw_request.user = self.test_user
        request = DRFRequest(raw_request)
        response = TruckListCreateAPIView().get(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["results"]), 5)

    def test_views_post_success_maps_command(self):
        fake_controller = self.makeSut(list_dtos=[])

        payload = {
            "license_plate": "ABC-1234",
            "brand": "Scania",
            "model": "FH 540",
            "manufacturing_year": 2020,
        }

        response = self.client.post("/api/trucks/", payload, format="json")
        self.assertEqual(response.status_code, 201)

        self.assertEqual(len(fake_controller.created_commands), 1)
        cmd = fake_controller.created_commands[0]
        self.assertEqual(cmd.license_plate, "ABC-1234")
        self.assertEqual(cmd.brand, "Scania")
        self.assertEqual(cmd.model, "FH 540")
        self.assertEqual(cmd.manufacturing_year, 2020)

    def test_views_put_success_maps_update_command(self):
        fake_controller = self.makeSut(list_dtos=[])

        truck_id = uuid4()
        payload = {"brand": "Scania", "model": "FH 540", "manufacturing_year": 2020}

        response = self.client.put(f"/api/trucks/{truck_id}/", payload, format="json")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(fake_controller.updated_calls), 1)
        called_id, cmd = fake_controller.updated_calls[0]
        self.assertEqual(called_id, truck_id)
        self.assertEqual(cmd.brand, "Scania")
        self.assertEqual(cmd.model, "FH 540")
        self.assertEqual(cmd.manufacturing_year, 2020)

    def test_exception_handler_duplicate_in_post(self):
        class _ErrorController(_FakeController):
            def create_truck(self, command: CreateTruckCommand) -> TruckDto:
                raise DuplicateLicensePlateError(command.license_plate)

        self.makeSut(controller_override=_ErrorController(list_dtos=[]))

        payload = {
            "license_plate": "ABC-1234",
            "brand": "Scania",
            "model": "FH 540",
            "manufacturing_year": 2020,
        }

        resp = self.client.post("/api/trucks/", payload, format="json")
        self.assertEqual(resp.status_code, 409)

    def test_exception_handler_truck_not_found_in_put(self):
        class _ErrorController(_FakeController):
            def update_truck(self, *, truck_id, command: UpdateTruckCommand) -> TruckDto:
                raise TruckNotFoundError(truck_id)

        self.makeSut(controller_override=_ErrorController(list_dtos=[]))

        truck_id = uuid4()
        payload = {"brand": "Scania", "model": "FH 540", "manufacturing_year": 2020}
        resp = self.client.put(f"/api/trucks/{truck_id}/", payload, format="json")
        self.assertEqual(resp.status_code, 404)
