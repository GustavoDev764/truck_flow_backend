from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response

from apps.trucks.domain.exceptions import (
    DuplicateLicensePlateError,
    InvalidFipeDataError,
    TruckNotFoundError,
)


class TruckErrorResponseFactory:
    """Factory responsável exclusivamente por converter exceções de domínio em responses HTTP."""

    @staticmethod
    def make(exc: Exception) -> Response:
        if isinstance(exc, DuplicateLicensePlateError):
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)

        if isinstance(exc, InvalidFipeDataError):
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)

        if isinstance(exc, TruckNotFoundError):
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        raise exc
