from __future__ import annotations

from django.test import SimpleTestCase
from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError

from apps.trucks.presentation.error_responses import TruckErrorResponseFactory
from apps.trucks.presentation.exception_handler import truck_exception_handler
from apps.trucks.presentation.serializers import TruckCreateSerializer


class ErrorsAndSerializersSpec(SimpleTestCase):
    def test_error_response_factory_raises_unknown_exception(self):
        with self.assertRaises(RuntimeError):
            TruckErrorResponseFactory.make(RuntimeError("boom"))

    def test_exception_handler_returns_drf_response_when_not_our_domain_error(self):
        resp = truck_exception_handler(DRFValidationError("invalid"), context={})
        self.assertIsNotNone(resp)
        self.assertEqual(resp.status_code, 400)

    def test_exception_handler_returns_none_for_unhandled_exceptions(self):
        resp = truck_exception_handler(ValueError("unhandled"), context={})
        self.assertIsNone(resp)

    def test_truck_create_serializer_license_plate_rejects_blank(self):
        serializer = TruckCreateSerializer()
        with self.assertRaises(serializers.ValidationError):
            serializer.validate_license_plate("   ")
