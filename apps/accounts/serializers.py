from datetime import datetime, timezone

from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.tokens import AccessToken
from rest_framework_simplejwt.tokens import RefreshToken

from apps.accounts.services.session_service import create_session


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Adiciona user na resposta e persiste sessão para invalidação no logout."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = CurrentUserSerializer(self.user).data

        # Persistir sessão para o access token (permite invalidação no logout)
        access_token = AccessToken(data["access"])
        jti = access_token.get("jti")
        exp = access_token.get("exp")
        if jti and exp:
            expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
            create_session(self.user, jti, expires_at)

        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    """Persiste sessão para o novo access token no refresh."""

    def validate(self, attrs):
        data = super().validate(attrs)
        access_token = AccessToken(data["access"])
        jti = access_token.get("jti")
        exp = access_token.get("exp")
        if jti and exp:
            from django.contrib.auth import get_user_model

            refresh = RefreshToken(attrs["refresh"])
            user_id = refresh.get("user_id")
            User = get_user_model()
            user = User.objects.get(pk=user_id) if user_id else None
            if user:
                expires_at = datetime.fromtimestamp(exp, tz=timezone.utc)
                create_session(user, jti, expires_at)
        return data


class CurrentUserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    groups = serializers.ListField(child=serializers.CharField())
    is_manage = serializers.BooleanField()

    def to_representation(self, instance):
        groups = list(instance.groups.values_list("name", flat=True))
        return {
            "id": instance.id,
            "username": instance.username,
            "groups": groups,
            "is_manage": "manage" in groups,
        }
