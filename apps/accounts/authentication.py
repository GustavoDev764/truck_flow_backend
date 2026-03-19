"""Autenticação JWT com validação de sessão."""

from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework_simplejwt.exceptions import InvalidToken

from apps.accounts.services.session_service import is_session_valid


class SessionAwareJWTAuthentication(JWTAuthentication):
    """JWT Authentication que verifica se a sessão foi revogada (logout)."""

    def get_validated_token(self, raw_token):
        token = super().get_validated_token(raw_token)
        jti = token.get("jti")
        if not jti or not is_session_valid(jti):
            raise InvalidToken({"detail": "Token inválido ou sessão encerrada."})
        return token
