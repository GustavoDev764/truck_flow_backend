from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response

from apps.accounts.presentation.serializers import UserSerializer


class UserResponseFactory:
    @staticmethod
    def list_users(dtos) -> Response:
        return Response([UserSerializer(dto).data for dto in dtos], status=status.HTTP_200_OK)

    @staticmethod
    def create_user(dto) -> Response:
        return Response(UserSerializer(dto).data, status=status.HTTP_201_CREATED)

    @staticmethod
    def update_user(dto) -> Response:
        return Response(UserSerializer(dto).data, status=status.HTTP_200_OK)

    @staticmethod
    def deactivate_user(dto) -> Response:
        return Response(UserSerializer(dto).data, status=status.HTTP_200_OK)
