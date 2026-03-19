from __future__ import annotations

from apps.accounts.application.dtos.commands import UserDto
from apps.accounts.domain.repositories import UserRepository


class ListUsersUseCase:
    def __init__(self, *, user_repo: UserRepository):
        self._user_repo = user_repo

    def execute(self) -> list[UserDto]:
        users = self._user_repo.list()
        return [self._to_dto(u) for u in users]

    def _to_dto(self, user) -> UserDto:
        return UserDto(
            id=user.id,
            username=user.username,
            email=user.email,
            first_name=user.first_name,
            last_name=user.last_name,
            is_active=user.is_active,
            groups_display=user.group_names,
            date_joined=user.date_joined,
        )
