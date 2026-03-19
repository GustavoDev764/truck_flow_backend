from __future__ import annotations

from typing import Protocol

from .entities import User


class UserRepository(Protocol):
    def get_by_id(self, user_id: int) -> User | None: ...

    def get_by_username(self, username: str) -> User | None: ...

    def list(self) -> list[User]: ...

    def create(
        self,
        *,
        username: str,
        email: str,
        password: str,
        first_name: str,
        last_name: str,
        group_names: list[str],
    ) -> User: ...

    def update(self, user: User) -> User: ...

    def update_password(self, *, user_id: int, new_password: str) -> None: ...

    def delete(self, user_id: int) -> None: ...
