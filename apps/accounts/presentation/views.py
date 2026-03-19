from __future__ import annotations

from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.accounts.dependencies import (
    make_change_password_command,
    make_create_user_command,
    make_deactivate_user_command,
    make_update_user_command,
    make_user_controller,
)
from apps.accounts.permissions import IsManage
from apps.accounts.presentation.response_factory import UserResponseFactory
from apps.accounts.presentation.serializers import (
    ChangePasswordSerializer,
    UserCreateSerializer,
    UserDeactivateSerializer,
    UserSerializer,
    UserUpdateSerializer,
)

_controller = make_user_controller()
_response_factory = UserResponseFactory()


class UserPageNumberPagination(PageNumberPagination):
    page_size = 10
    page_size_query_param = "page_size"


class UserListCreateAPIView(APIView):
    permission_classes = [IsManage]

    def get(self, request):
        dtos = _controller.list_users()
        paginator = UserPageNumberPagination()
        page = paginator.paginate_queryset(dtos, request, view=self)
        data = [UserSerializer(dto).data for dto in page]
        return paginator.get_paginated_response(data)

    def post(self, request):
        serializer = UserCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        command = make_create_user_command(payload)
        dto = _controller.create_user(command)
        return _response_factory.create_user(dto)


class UserDetailAPIView(APIView):
    permission_classes = [IsManage]

    def get(self, request, user_id):
        dto = _controller.get_user(user_id)
        return Response(UserSerializer(dto).data)

    def put(self, request, user_id):
        serializer = UserUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        command = make_update_user_command(payload)
        dto = _controller.update_user(user_id=user_id, command=command)
        return _response_factory.update_user(dto)

    def patch(self, request, user_id):
        dto = _controller.get_user(user_id)
        existing = {
            "email": dto.email,
            "first_name": dto.first_name,
            "last_name": dto.last_name,
            "groups": list(dto.groups_display),
        }
        merged = {**existing, **request.data}
        serializer = UserUpdateSerializer(data=merged, partial=True)
        serializer.is_valid(raise_exception=True)
        command = make_update_user_command(serializer.validated_data)
        dto = _controller.update_user(user_id=user_id, command=command)
        return _response_factory.update_user(dto)


class UserDeactivateAPIView(APIView):
    permission_classes = [IsManage]

    def patch(self, request, user_id):
        serializer = UserDeactivateSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        command = make_deactivate_user_command(payload)
        dto = _controller.deactivate_user(user_id=user_id, command=command)
        return _response_factory.deactivate_user(dto)


class UserChangePasswordAPIView(APIView):
    permission_classes = [IsManage]

    def post(self, request, user_id):
        serializer = ChangePasswordSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        payload = serializer.validated_data
        command = make_change_password_command(payload)
        _controller.change_password(user_id=user_id, command=command)
        return Response({"detail": "Senha alterada com sucesso."})

