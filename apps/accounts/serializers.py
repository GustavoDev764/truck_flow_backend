from rest_framework import serializers
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    """Adiciona user (id, username, groups, is_manage) na resposta do login."""

    def validate(self, attrs):
        data = super().validate(attrs)
        data["user"] = CurrentUserSerializer(self.user).data
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
