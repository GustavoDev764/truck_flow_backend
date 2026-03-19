from __future__ import annotations

from apps.accounts.application.dtos.commands import CreateUserCommand, UserDto
from apps.accounts.domain.exceptions import DuplicateUsernameError
from apps.accounts.domain.repositories import UserRepository


class CreateUserUseCase:
    def __init__(self, *, user_repo: UserRepository):
        self._user_repo = user_repo

    def execute(self, command: CreateUserCommand) -> UserDto:
        existing = self._user_repo.get_by_username(command.username)
        if existing is not None:
            raise DuplicateUsernameError(command.username)

        user = self._user_repo.create(
            username=command.username,
            email=command.email,
            password=command.password,
            first_name=command.first_name,
            last_name=command.last_name,
            group_names=list(command.group_names),
        )
        return self._to_dto(user)

    def _to_dto(self, user) -> UserDto:
        from apps.accounts.domain.entities import User as UserEntity

        u: UserEntity = user
        return UserDto(
            id=u.id,
            username=u.username,
            email=u.email,
            first_name=u.first_name,
            last_name=u.last_name,
            is_active=u.is_active,
            groups_display=u.group_names,
            date_joined=u.date_joined,
        )
