from __future__ import annotations

from decimal import Decimal
from unittest.mock import MagicMock, patch
from uuid import UUID, uuid4

from django.test import SimpleTestCase
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
from apps.trucks.presentation.views import (
    FipeBrandsAPIView,
    FipeModelsAPIView,
    FipeYearsAPIView,
    TruckListCreateAPIView,
)


def _make_user_spy() -> MagicMock:
    """Spy de usuário autenticado no grupo cliente (sem banco)."""
    user = MagicMock()
    user.is_authenticated = True
    user.groups.filter.return_value.exists.return_value = True
    return user


class TruckControllerSpy:
    def __init__(self, *, list_dtos: list[TruckDto]):
        self._list_dtos = list_dtos
        self.created_commands: list[CreateTruckCommand] = []
        self.updated_calls: list[tuple[UUID, UpdateTruckCommand]] = []
        self.deleted_ids: list[UUID] = []

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
        self.deleted_ids.append(truck_id)


class PresentationViewsSpec(SimpleTestCase):
    def setUp(self) -> None:
        self.client = APIClient()
        self.factory = APIRequestFactory()
        self.test_user = _make_user_spy()
        self.client.force_authenticate(user=self.test_user)

    def makeSut(
        self,
        *,
        list_dtos: list[TruckDto] | None = None,
        controller_override: TruckControllerSpy | None = None,
    ) -> TruckControllerSpy:
        if controller_override is not None:
            controller_spy = controller_override
        else:
            list_dtos = list_dtos or []
            controller_spy = TruckControllerSpy(list_dtos=list_dtos)

        import apps.trucks.presentation.views as views_module

        views_module._controller = controller_spy
        return controller_spy

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
        controller_spy = self.makeSut(list_dtos=[])

        payload = {
            "license_plate": "ABC-1234",
            "brand": "Scania",
            "model": "FH 540",
            "manufacturing_year": 2020,
        }

        response = self.client.post("/api/trucks/", payload, format="json")
        self.assertEqual(response.status_code, 201)

        self.assertEqual(len(controller_spy.created_commands), 1)
        cmd = controller_spy.created_commands[0]
        self.assertEqual(cmd.license_plate, "ABC-1234")
        self.assertEqual(cmd.brand, "Scania")
        self.assertEqual(cmd.model, "FH 540")
        self.assertEqual(cmd.manufacturing_year, 2020)

    def test_views_put_success_maps_update_command(self):
        controller_spy = self.makeSut(list_dtos=[])

        truck_id = uuid4()
        payload = {"brand": "Scania", "model": "FH 540", "manufacturing_year": 2020}

        response = self.client.put(f"/api/trucks/{truck_id}/", payload, format="json")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(len(controller_spy.updated_calls), 1)
        called_id, cmd = controller_spy.updated_calls[0]
        self.assertEqual(called_id, truck_id)
        self.assertEqual(cmd.brand, "Scania")
        self.assertEqual(cmd.model, "FH 540")
        self.assertEqual(cmd.manufacturing_year, 2020)

    def test_exception_handler_duplicate_in_post(self):
        class _ErrorController(TruckControllerSpy):
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
        class _ErrorController(TruckControllerSpy):
            def update_truck(self, *, truck_id, command: UpdateTruckCommand) -> TruckDto:
                raise TruckNotFoundError(truck_id)

        self.makeSut(controller_override=_ErrorController(list_dtos=[]))

        truck_id = uuid4()
        payload = {"brand": "Scania", "model": "FH 540", "manufacturing_year": 2020}
        resp = self.client.put(f"/api/trucks/{truck_id}/", payload, format="json")
        self.assertEqual(resp.status_code, 404)

    def test_views_delete_success(self):
        controller_spy = self.makeSut(list_dtos=[])
        truck_id = uuid4()

        response = self.client.delete(f"/api/trucks/{truck_id}/")
        self.assertEqual(response.status_code, 204)
        self.assertEqual(controller_spy.deleted_ids, [truck_id])

    @patch("apps.trucks.presentation.views._fipe_client")
    def test_fipe_brands_returns_data(self, mock_fipe):
        mock_fipe.get_brands.return_value = [{"id": "1", "name": "Scania"}]
        raw_request = self.factory.get("/api/fipe/brands/")
        raw_request.user = self.test_user
        from rest_framework.request import Request as DRFRequest

        request = DRFRequest(raw_request)
        response = FipeBrandsAPIView().get(request)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"id": "1", "name": "Scania"}])

    @patch("apps.trucks.presentation.views._fipe_client")
    def test_fipe_models_returns_data(self, mock_fipe):
        mock_fipe.get_models.return_value = [{"id": "1", "name": "FH 540"}]
        raw_request = self.factory.get("/api/fipe/brands/1/models/")
        raw_request.user = self.test_user
        from rest_framework.request import Request as DRFRequest

        request = DRFRequest(raw_request)
        response = FipeModelsAPIView().get(request, brand_id="1")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"id": "1", "name": "FH 540"}])

    @patch("apps.trucks.presentation.views._fipe_client")
    def test_fipe_years_returns_data(self, mock_fipe):
        mock_fipe.get_years.return_value = [{"year": 2020}]
        raw_request = self.factory.get("/api/fipe/brands/1/models/2/years/")
        raw_request.user = self.test_user
        from rest_framework.request import Request as DRFRequest

        request = DRFRequest(raw_request)
        response = FipeYearsAPIView().get(request, brand_id="1", model_id="2")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, [{"year": 2020}])

    @patch("apps.trucks.presentation.views._fipe_client")
    def test_fipe_brands_handles_exception(self, mock_fipe):
        mock_fipe.get_brands.side_effect = RuntimeError("FIPE indisponível")
        raw_request = self.factory.get("/api/fipe/brands/")
        raw_request.user = self.test_user
        from rest_framework.request import Request as DRFRequest

        request = DRFRequest(raw_request)
        response = FipeBrandsAPIView().get(request)
        self.assertEqual(response.status_code, 500)

    @patch("apps.trucks.presentation.views._fipe_client")
    def test_fipe_models_handles_exception(self, mock_fipe):
        mock_fipe.get_models.side_effect = RuntimeError("FIPE indisponível")
        raw_request = self.factory.get("/api/fipe/brands/1/models/")
        raw_request.user = self.test_user
        from rest_framework.request import Request as DRFRequest

        request = DRFRequest(raw_request)
        response = FipeModelsAPIView().get(request, brand_id="1")
        self.assertEqual(response.status_code, 500)

    @patch("apps.trucks.presentation.views._fipe_client")
    def test_fipe_years_handles_exception(self, mock_fipe):
        mock_fipe.get_years.side_effect = RuntimeError("FIPE indisponível")
        raw_request = self.factory.get("/api/fipe/brands/1/models/2/years/")
        raw_request.user = self.test_user
        from rest_framework.request import Request as DRFRequest

        request = DRFRequest(raw_request)
        response = FipeYearsAPIView().get(request, brand_id="1", model_id="2")
        self.assertEqual(response.status_code, 500)
