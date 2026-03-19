from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response

from apps.trucks.presentation.serializers import TruckSerializer


class TruckResponseFactory:
    """Factory responsável por montar responses de sucesso (DTO -> serializer -> Response)."""

    @staticmethod
    def list_trucks(dtos) -> Response:
        return Response([TruckSerializer(dto).data for dto in dtos], status=status.HTTP_200_OK)

    @staticmethod
    def create_truck(dto) -> Response:
        return Response(TruckSerializer(dto).data, status=status.HTTP_201_CREATED)

    @staticmethod
    def update_truck(dto) -> Response:
        return Response(TruckSerializer(dto).data, status=status.HTTP_200_OK)
