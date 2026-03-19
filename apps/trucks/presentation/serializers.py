from __future__ import annotations

from datetime import datetime

from rest_framework import serializers


def _normalize_plate(value: str) -> str:
    return value.strip().upper()


class TruckCreateSerializer(serializers.Serializer):
    license_plate = serializers.CharField(max_length=16)
    brand = serializers.CharField(max_length=255)
    model = serializers.CharField(max_length=255)
    manufacturing_year = serializers.IntegerField()

    def validate_license_plate(self, value: str) -> str:
        normalized = _normalize_plate(value)
        if not normalized:
            raise serializers.ValidationError("Placa inválida.")
        return normalized

    def validate_manufacturing_year(self, value: int) -> int:
        current_year = datetime.utcnow().year
        if value < 1900 or value > current_year + 1:
            raise serializers.ValidationError("Ano de fabricação fora do intervalo permitido.")
        return value


class TruckUpdateSerializer(serializers.Serializer):
    brand = serializers.CharField(max_length=255)
    model = serializers.CharField(max_length=255)
    manufacturing_year = serializers.IntegerField()

    def validate_manufacturing_year(self, value: int) -> int:
        current_year = datetime.utcnow().year
        if value < 1900 or value > current_year + 1:
            raise serializers.ValidationError("Ano de fabricação fora do intervalo permitido.")
        return value


class TruckSerializer(serializers.Serializer):
    id = serializers.UUIDField()
    license_plate = serializers.CharField(max_length=16)
    brand = serializers.CharField(max_length=255)
    model = serializers.CharField(max_length=255)
    manufacturing_year = serializers.IntegerField()
    fipe_price = serializers.DecimalField(max_digits=12, decimal_places=2)
