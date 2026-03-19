"""Serviço de sessões JWT."""

import uuid

from django.utils import timezone

from apps.accounts.models import Session


def _parse_jti(jti) -> uuid.UUID:
    """Converte jti para UUID (aceita hex string ou UUID)."""
    if isinstance(jti, uuid.UUID):
        return jti
    s = str(jti)
    if len(s) == 32 and all(c in "0123456789abcdefABCDEF" for c in s):
        return uuid.UUID(hex=s)
    return uuid.UUID(s)


def create_session(user, jti, expires_at) -> Session:
    """Cria uma sessão para o token JWT."""
    return Session.objects.create(
        user=user,
        jti=_parse_jti(jti),
        expires_at=expires_at,
        revoked=False,
    )


def revoke_session_by_jti(jti) -> bool:
    """Marca sessão como revogada pelo jti. Retorna True se encontrou e revogou."""
    jti_uuid = _parse_jti(jti)
    updated = Session.objects.filter(jti=jti_uuid).update(revoked=True)
    return updated > 0


def is_session_valid(jti) -> bool:
    """Verifica se a sessão existe, não está revogada e não expirou."""
    jti_uuid = _parse_jti(jti)
    now = timezone.now()
    return Session.objects.filter(
        jti=jti_uuid,
        revoked=False,
        expires_at__gt=now,
    ).exists()
