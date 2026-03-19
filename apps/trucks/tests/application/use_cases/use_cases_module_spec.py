from __future__ import annotations

from django.test import SimpleTestCase


class UseCasesModuleReexportSpec(SimpleTestCase):
    def test_use_cases_module_reexport_imports(self):
        import apps.trucks.application.use_cases as use_cases_module

        self.assertTrue(hasattr(use_cases_module, "CreateTruckUseCase"))
        self.assertTrue(hasattr(use_cases_module, "ListTrucksUseCase"))
        self.assertTrue(hasattr(use_cases_module, "UpdateTruckUseCase"))
