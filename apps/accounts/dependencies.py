from __future__ import annotations

from apps.accounts.application.dtos.commands import (
    ChangePasswordCommand,
    CreateUserCommand,
    DeactivateUserCommand,
    UpdateUserCommand,
)
from apps.accounts.application.services.user_controller import UserController
from apps.accounts.application.use_cases.change_password_use_case import ChangePasswordUseCase
from apps.accounts.application.use_cases.create_user_use_case import CreateUserUseCase
from apps.accounts.application.use_cases.deactivate_user_use_case import DeactivateUserUseCase
from apps.accounts.application.use_cases.get_user_use_case import GetUserUseCase
from apps.accounts.application.use_cases.list_users_use_case import ListUsersUseCase
from apps.accounts.application.use_cases.update_user_use_case import UpdateUserUseCase
from apps.accounts.infrastructure.persistence.repositories import DjangoUserRepository


def make_user_controller() -> UserController:
    user_repo = DjangoUserRepository()
    return UserController(
        list_users_use_case=ListUsersUseCase(user_repo=user_repo),
        get_user_use_case=GetUserUseCase(user_repo=user_repo),
        create_user_use_case=CreateUserUseCase(user_repo=user_repo),
        update_user_use_case=UpdateUserUseCase(user_repo=user_repo),
        deactivate_user_use_case=DeactivateUserUseCase(user_repo=user_repo),
        change_password_use_case=ChangePasswordUseCase(user_repo=user_repo),
    )


def make_create_user_command(payload: dict) -> CreateUserCommand:
    return CreateUserCommand(
        username=payload["username"],
        email=payload.get("email", ""),
        password=payload["password"],
        first_name=payload.get("first_name", ""),
        last_name=payload.get("last_name", ""),
        group_names=tuple(payload.get("groups", [])),
    )


def make_update_user_command(payload: dict) -> UpdateUserCommand:
    groups = payload.get("groups") or []
    return UpdateUserCommand(
        email=payload.get("email", ""),
        first_name=payload.get("first_name", ""),
        last_name=payload.get("last_name", ""),
        group_names=tuple(groups),
    )


def make_deactivate_user_command(payload: dict) -> DeactivateUserCommand:
    return DeactivateUserCommand(is_active=payload["is_active"])


def make_change_password_command(payload: dict) -> ChangePasswordCommand:
    return ChangePasswordCommand(new_password=payload["new_password"])
