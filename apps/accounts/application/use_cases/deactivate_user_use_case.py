from __future__ import annotations

from apps.accounts.application.dtos.commands import DeactivateUserCommand, UserDto
from apps.accounts.domain.exceptions import UserNotFoundError
from apps.accounts.domain.repositories import UserRepository


class DeactivateUserUseCase:
    def __init__(self, *, user_repo: UserRepository):
        self._user_repo = user_repo

    def execute(self, *, user_id: int, command: DeactivateUserCommand) -> UserDto:
        existing = self._user_repo.get_by_id(user_id)
        if existing is None:
            raise UserNotFoundError(user_id)

        updated = existing.with_updated_active(is_active=command.is_active)
        saved = self._user_repo.update(updated)
        return self._to_dto(saved)

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
