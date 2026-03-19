from __future__ import annotations

from apps.accounts.domain.exceptions import UserNotFoundError
from apps.accounts.domain.repositories import UserRepository


class ChangePasswordUseCase:
    def __init__(self, *, user_repo: UserRepository):
        self._user_repo = user_repo

    def execute(self, *, user_id: int, new_password: str) -> None:
        existing = self._user_repo.get_by_id(user_id)
        if existing is None:
            raise UserNotFoundError(user_id)

        self._user_repo.update_password(user_id=user_id, new_password=new_password)
