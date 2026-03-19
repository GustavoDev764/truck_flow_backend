"""Mocks/fakes usados nos testes de application."""

from apps.trucks.tests.application.mocks.truck_use_case_spy import (
    FipeClientGenericErrorSpy,
    FipeClientSpy,
    TruckRepositorySpy,
)

__all__ = ["TruckRepositorySpy", "FipeClientSpy", "FipeClientGenericErrorSpy"]
