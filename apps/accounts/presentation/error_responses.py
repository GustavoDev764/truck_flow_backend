from __future__ import annotations

from rest_framework import status
from rest_framework.response import Response

from apps.accounts.domain.exceptions import DuplicateUsernameError, UserNotFoundError


class UserErrorResponseFactory:
    @staticmethod
    def make(exc: Exception) -> Response:
        if isinstance(exc, UserNotFoundError):
            return Response({"detail": str(exc)}, status=status.HTTP_404_NOT_FOUND)

        if isinstance(exc, DuplicateUsernameError):
            return Response({"detail": str(exc)}, status=status.HTTP_409_CONFLICT)

        raise exc
