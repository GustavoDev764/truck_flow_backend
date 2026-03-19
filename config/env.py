from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

_ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(_ROOT_DIR / ".env")


def _get_str(name: str, default: str = "") -> str:
    value = os.getenv(name, default)
    return value if value is not None else default


def _get_int(name: str, default: int) -> int:
    value = os.getenv(name)
    if value is None:
        return default
    try:
        return int(str(value).strip())
    except Exception:
        return default


@dataclass(frozen=True)
class EnvConfig:

    HOST_PORT: int

    DJANGO_ENV: str
    DEBUG: str

    DB_PROVIDER: str
    DB_HOST: str
    DB_PORT: int
    DB_USER: str
    DB_PASSWORD: str
    DB_NAME: str

    FIPE_BASE_URL: str
    FIPE_TRUCK_VEHICLE_TYPE: str
    FIPE_APP_URL_TEMPLATE: str

    JWT_SECRET: str
    JWT_EXPIRES_IN: str

    REDIS_HOST: str
    REDIS_PORT: int

    UPLOAD_PATH: str
    STORAGE_PATH: str


def _build_env() -> EnvConfig:
    return EnvConfig(
        HOST_PORT=_get_int("HOST_PORT", 3000),
        DJANGO_ENV=_get_str("DJANGO_ENV", ""),
        DEBUG=_get_str("DEBUG", ""),
        DB_PROVIDER=_get_str("DB_PROVIDER", "postgres").strip().lower(),
        DB_HOST=_get_str("DB_HOST", "localhost"),
        DB_PORT=_get_int("DB_PORT", 5432),
        DB_USER=_get_str("DB_USER", "postgres"),
        DB_PASSWORD=_get_str("DB_PASSWORD", ""),
        DB_NAME=_get_str("DB_NAME", ""),
        FIPE_BASE_URL=_get_str("FIPE_BASE_URL", "https://fipe.parallelum.com.br/api/v2"),
        FIPE_TRUCK_VEHICLE_TYPE=_get_str("FIPE_TRUCK_VEHICLE_TYPE", "trucks"),
        FIPE_APP_URL_TEMPLATE=_get_str("FIPE_APP_URL_TEMPLATE", "app.fipe/{placa}/modelo/{modelo}"),
        JWT_SECRET=_get_str("JWT_SECRET", ""),
        JWT_EXPIRES_IN=_get_str("JWT_EXPIRES_IN", "7d"),
        REDIS_HOST=_get_str("REDIS_HOST", "localhost"),
        REDIS_PORT=_get_int("REDIS_PORT", 6379),
        UPLOAD_PATH=_get_str("UPLOAD_PATH", "./uploads"),
        STORAGE_PATH=_get_str("STORAGE_PATH", "./storage"),
    )


env: EnvConfig = _build_env()
