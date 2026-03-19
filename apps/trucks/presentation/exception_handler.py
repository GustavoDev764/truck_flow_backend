from __future__ import annotations

from rest_framework.views import exception_handler as drf_exception_handler

from apps.trucks.domain.exceptions import (
    DuplicateLicensePlateError,
    InvalidFipeDataError,
    TruckNotFoundError,
)
from apps.trucks.presentation.error_responses import TruckErrorResponseFactory


def truck_exception_handler(exc: Exception, context):
    """
    Centraliza a tradução de erros de domínio para respostas HTTP.

    Observação: exceções de validação do DRF continuam sendo tratadas pelo próprio DRF.
    """

    response = drf_exception_handler(exc, context)
    if response is not None:
        return response

    if isinstance(exc, (DuplicateLicensePlateError, InvalidFipeDataError, TruckNotFoundError)):
        return TruckErrorResponseFactory.make(exc)

    return None
