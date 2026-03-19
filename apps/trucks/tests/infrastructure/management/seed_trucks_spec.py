from __future__ import annotations

import unittest.mock as mock

from django.core.management import call_command
from django.test import SimpleTestCase


class SeedTrucksCommandSpec(SimpleTestCase):
    def test_seed_trucks_runs_and_uses_update_or_create(self):
        with mock.patch("apps.trucks.management.commands.seed_trucks.TruckModel") as TruckModelMock:
            TruckModelMock.objects.update_or_create.return_value = (object(), True)
            call_command("seed_trucks")

            self.assertEqual(TruckModelMock.objects.update_or_create.call_count, 3)

    def test_seed_trucks_clear_flag_calls_delete(self):
        with mock.patch("apps.trucks.management.commands.seed_trucks.TruckModel") as TruckModelMock:
            TruckModelMock.objects.update_or_create.return_value = (object(), True)
            call_command("seed_trucks", "--clear")
            TruckModelMock.objects.all.assert_called()
            TruckModelMock.objects.all.return_value.delete.assert_called()

    def test_seed_trucks_updates_when_is_created_false(self):
        with mock.patch("apps.trucks.management.commands.seed_trucks.TruckModel") as TruckModelMock:
            TruckModelMock.objects.update_or_create.side_effect = [
                (object(), True),
                (object(), False),
                (object(), False),
            ]
            call_command("seed_trucks")
            self.assertEqual(TruckModelMock.objects.update_or_create.call_count, 3)
