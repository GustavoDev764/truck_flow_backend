from __future__ import annotations

from rest_framework import serializers


class UserCreateSerializer(serializers.Serializer):
    username = serializers.CharField(max_length=150)
    email = serializers.EmailField(required=False, allow_blank=True, default="")
    password = serializers.CharField(min_length=8, write_only=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True, default="")
    groups = serializers.ListField(
        child=serializers.CharField(), required=False, allow_empty=True, default=list
    )


class UserUpdateSerializer(serializers.Serializer):
    email = serializers.EmailField(required=False, allow_blank=True)
    first_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    last_name = serializers.CharField(max_length=150, required=False, allow_blank=True)
    groups = serializers.ListField(child=serializers.CharField(), required=False, allow_empty=True)


class UserSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    username = serializers.CharField()
    email = serializers.CharField()
    first_name = serializers.CharField()
    last_name = serializers.CharField()
    is_active = serializers.BooleanField()
    groups_display = serializers.ListField(child=serializers.CharField())
    date_joined = serializers.DateTimeField()


class UserDeactivateSerializer(serializers.Serializer):
    is_active = serializers.BooleanField()


class ChangePasswordSerializer(serializers.Serializer):
    new_password = serializers.CharField(min_length=8, write_only=True)
