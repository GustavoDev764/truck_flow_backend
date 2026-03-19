from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class CreateUserCommand:
    username: str
    email: str
    password: str
    first_name: str
    last_name: str
    group_names: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class UpdateUserCommand:
    email: str
    first_name: str
    last_name: str
    group_names: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class DeactivateUserCommand:
    is_active: bool


@dataclass(frozen=True, slots=True)
class ChangePasswordCommand:
    new_password: str


@dataclass(frozen=True, slots=True)
class UserDto:
    id: int
    username: str
    email: str
    first_name: str
    last_name: str
    is_active: bool
    groups_display: tuple[str, ...]
    date_joined: datetime
