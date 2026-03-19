"""
Exception handler centralizado para a API.
Trata exceções de domínio dos módulos trucks e accounts.
"""

from __future__ import annotations

from rest_framework.views import exception_handler as drf_exception_handler

from apps.accounts.domain.exceptions import DuplicateUsernameError, UserNotFoundError
from apps.accounts.presentation.error_responses import UserErrorResponseFactory
from apps.trucks.domain.exceptions import (
    DuplicateLicensePlateError,
    InvalidFipeDataError,
    TruckNotFoundError,
)
from apps.trucks.presentation.error_responses import TruckErrorResponseFactory


def api_exception_handler(exc: Exception, context):
    response = drf_exception_handler(exc, context)
    if response is not None:
        return response

    if isinstance(exc, (UserNotFoundError, DuplicateUsernameError)):
        return UserErrorResponseFactory.make(exc)

    if isinstance(exc, (DuplicateLicensePlateError, InvalidFipeDataError, TruckNotFoundError)):
        return TruckErrorResponseFactory.make(exc)

    return None
