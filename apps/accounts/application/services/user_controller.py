from __future__ import annotations

from apps.accounts.application.dtos.commands import (
    ChangePasswordCommand,
    CreateUserCommand,
    DeactivateUserCommand,
    UpdateUserCommand,
    UserDto,
)
from apps.accounts.application.use_cases.change_password_use_case import ChangePasswordUseCase
from apps.accounts.application.use_cases.create_user_use_case import CreateUserUseCase
from apps.accounts.application.use_cases.deactivate_user_use_case import DeactivateUserUseCase
from apps.accounts.application.use_cases.get_user_use_case import GetUserUseCase
from apps.accounts.application.use_cases.list_users_use_case import ListUsersUseCase
from apps.accounts.application.use_cases.update_user_use_case import UpdateUserUseCase


class UserController:
    def __init__(
        self,
        *,
        list_users_use_case: ListUsersUseCase,
        get_user_use_case: GetUserUseCase,
        create_user_use_case: CreateUserUseCase,
        update_user_use_case: UpdateUserUseCase,
        deactivate_user_use_case: DeactivateUserUseCase,
        change_password_use_case: ChangePasswordUseCase,
    ):
        self._list_users_use_case = list_users_use_case
        self._get_user_use_case = get_user_use_case
        self._create_user_use_case = create_user_use_case
        self._update_user_use_case = update_user_use_case
        self._deactivate_user_use_case = deactivate_user_use_case
        self._change_password_use_case = change_password_use_case

    def list_users(self) -> list[UserDto]:
        return self._list_users_use_case.execute()

    def get_user(self, user_id: int) -> UserDto:
        return self._get_user_use_case.execute(user_id)

    def create_user(self, command: CreateUserCommand) -> UserDto:
        return self._create_user_use_case.execute(command)

    def update_user(self, *, user_id: int, command: UpdateUserCommand) -> UserDto:
        return self._update_user_use_case.execute(user_id=user_id, command=command)

    def deactivate_user(self, *, user_id: int, command: DeactivateUserCommand) -> UserDto:
        return self._deactivate_user_use_case.execute(user_id=user_id, command=command)

    def change_password(self, *, user_id: int, command: ChangePasswordCommand) -> None:
        self._change_password_use_case.execute(user_id=user_id, new_password=command.new_password)
