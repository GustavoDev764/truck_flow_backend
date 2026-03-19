from __future__ import annotations

import unittest.mock as mock

from django.core.management import call_command
from django.test import SimpleTestCase

from apps.trucks.management.commands.seed_trucks import SEEDS


def _truck_model_spy(pk: int = 1) -> mock.MagicMock:
    """Spy de TruckModel: objeto mock com pk para update_or_create (sem banco)."""
    obj = mock.MagicMock()
    obj.pk = pk
    return obj


class SeedTrucksCommandSpec(SimpleTestCase):
    def test_seed_trucks_runs_and_uses_update_or_create(self):
        with mock.patch("apps.trucks.management.commands.seed_trucks.TruckModel") as TruckModelMock:
            TruckModelMock.objects.update_or_create.return_value = (_truck_model_spy(), True)
            call_command("seed_trucks")

            self.assertEqual(TruckModelMock.objects.update_or_create.call_count, len(SEEDS))

    def test_seed_trucks_clear_flag_calls_delete(self):
        with mock.patch("apps.trucks.management.commands.seed_trucks.TruckModel") as TruckModelMock:
            TruckModelMock.objects.update_or_create.return_value = (_truck_model_spy(), True)
            TruckModelMock.objects.all.return_value.delete.return_value = 0
            call_command("seed_trucks", "--clear")
            TruckModelMock.objects.all.assert_called()
            TruckModelMock.objects.all.return_value.delete.assert_called()

    def test_seed_trucks_updates_when_is_created_false(self):
        n = len(SEEDS)
        with mock.patch("apps.trucks.management.commands.seed_trucks.TruckModel") as TruckModelMock:
            TruckModelMock.objects.update_or_create.side_effect = [
                (_truck_model_spy(1), True),
                (_truck_model_spy(2), False),
                (_truck_model_spy(3), False),
            ] + [(_truck_model_spy(i), True) for i in range(4, n + 1)]
            call_command("seed_trucks")
            self.assertEqual(TruckModelMock.objects.update_or_create.call_count, n)
