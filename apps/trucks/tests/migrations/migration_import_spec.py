from __future__ import annotations

import importlib

from django.test import SimpleTestCase


class MigrationImportSpec(SimpleTestCase):
    def test_can_import_migration_module_for_coverage(self):
        importlib.import_module("apps.trucks.migrations.0001_initial")

