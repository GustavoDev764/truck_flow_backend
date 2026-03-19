from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class User:
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    group_names: tuple[str, ...]
    date_joined: datetime

    def with_updated_profile(
        self,
        *,
        email: str,
        first_name: str,
        last_name: str,
        group_names: tuple[str, ...],
    ) -> User:
        return User(
            id=self.id,
            username=self.username,
            email=email,
            first_name=first_name,
            last_name=last_name,
            is_active=self.is_active,
            group_names=group_names,
            date_joined=self.date_joined,
        )

    def with_updated_active(self, *, is_active: bool) -> User:
        return User(
            id=self.id,
            username=self.username,
            email=self.email,
            first_name=self.first_name,
            last_name=self.last_name,
            is_active=is_active,
            group_names=self.group_names,
            date_joined=self.date_joined,
        )
