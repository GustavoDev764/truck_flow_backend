from __future__ import annotations

from apps.accounts.application.dtos.commands import UserDto
from apps.accounts.domain.exceptions import UserNotFoundError
from apps.accounts.domain.repositories import UserRepository


class GetUserUseCase:
    def __init__(self, *, user_repo: UserRepository):
        self._user_repo = user_repo

    def execute(self, user_id: int) -> UserDto:
        user = self._user_repo.get_by_id(user_id)
        if user is None:
            raise UserNotFoundError(user_id)
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
