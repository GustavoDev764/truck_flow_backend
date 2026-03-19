from __future__ import annotations

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.permissions import IsClienteOrManage
from apps.trucks.dependencies import make_controller_entity, make_create_entity, make_update_entity
from apps.trucks.infrastructure.fipe.client import FipeClientHttp
from apps.trucks.presentation.exception_handler import truck_exception_handler
from apps.trucks.presentation.response_factory import TruckResponseFactory
from apps.trucks.presentation.serializers import (
    TruckCreateSerializer,
    TruckSerializer,
    TruckUpdateSerializer,
)

_controller = make_controller_entity()
_response_factory = TruckResponseFactory()
_fipe_client = FipeClientHttp()


class TruckListCreateAPIView(APIView):
    permission_classes = [IsClienteOrManage]

    def get(self, request):
        dtos = _controller.list_trucks()
        paginator = PageNumberPagination()
        paginator.page_size = 10

        page = paginator.paginate_queryset(dtos, request, view=self)
        data = [TruckSerializer(dto).data for dto in page]
        return paginator.get_paginated_response(data)

    def post(self, request):
        serializer = TruckCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        payload = serializer.validated_data
        command = make_create_entity(payload)
        dto = _controller.create_truck(command)
        return _response_factory.create_truck(dto)


class TruckUpdateAPIView(APIView):
    permission_classes = [IsClienteOrManage]

    def put(self, request, truck_id):
        serializer = TruckUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data

        command = make_update_entity(payload)
        dto = _controller.update_truck(truck_id=truck_id, command=command)
        return _response_factory.update_truck(dto)

    def delete(self, request, truck_id):
        _controller.delete_truck(truck_id)
        return Response(status=204)


class FipeBrandsAPIView(APIView):
    """Lista marcas disponíveis na tabela FIPE."""

    permission_classes = [IsClienteOrManage]

    def get(self, request):
        try:
            data = _fipe_client.get_brands()
            return Response(data)
        except Exception as exc:
            resp = truck_exception_handler(exc, {"request": request})
            return resp if resp is not None else Response({"detail": str(exc)}, status=500)


class FipeModelsAPIView(APIView):
    """Lista modelos da marca na tabela FIPE."""

    permission_classes = [IsClienteOrManage]

    def get(self, request, brand_id):
        try:
            data = _fipe_client.get_models(brand_id)
            return Response(data)
        except Exception as exc:
            resp = truck_exception_handler(exc, {"request": request})
            return resp if resp is not None else Response({"detail": str(exc)}, status=500)


class FipeYearsAPIView(APIView):
    """Lista anos disponíveis para o modelo na tabela FIPE."""

    permission_classes = [IsClienteOrManage]

    def get(self, request, brand_id, model_id):
        try:
            data = _fipe_client.get_years(brand_id, model_id)
            return Response(data)
        except Exception as exc:
            resp = truck_exception_handler(exc, {"request": request})
            return resp if resp is not None else Response({"detail": str(exc)}, status=500)
