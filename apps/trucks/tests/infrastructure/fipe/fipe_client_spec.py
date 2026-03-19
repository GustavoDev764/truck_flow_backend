from __future__ import annotations

import re
import unittest.mock as mock
from dataclasses import dataclass
from decimal import Decimal

import requests
from django.test import SimpleTestCase

from apps.trucks.domain.exceptions import InvalidFipeDataError
from apps.trucks.infrastructure.fipe import client as fipe_client_module
from apps.trucks.infrastructure.fipe.client import FipeClientHttp


@dataclass
class _FakeResponse:
    status_code: int
    payload: object
    json_exc: Exception | None = None

    def json(self):
        if self.json_exc is not None:
            raise self.json_exc
        return self.payload


class _SequencedFakeSession:
    def __init__(self, *, behaviors: dict[str, _FakeResponse], raise_on: set[str] | None = None):
        self._behaviors = behaviors
        self._raise_on = raise_on or set()

    def get(self, url, params=None, timeout=None):
        if url in self._raise_on:
            raise requests.RequestException("Falha simulada de rede.")

        _ = params, timeout

        for key, resp in self._behaviors.items():
            if re.fullmatch(key, url):
                return resp

        raise AssertionError(f"Endpoint não mapeado no FakeSession: {url}")


class FipeClientSpec(SimpleTestCase):
    def test_get_fipe_price_success_and_caches(self):
        base_url = fipe_client_module.FIPE_BASE_URL
        vehicle_type = fipe_client_module.FIPE_TRUCK_VEHICLE_TYPE

        behaviors = {
            rf"{re.escape(base_url)}/references": _FakeResponse(
                status_code=200,
                payload=[
                    {"code": "307", "month": "março de 2024"},
                    {"code": "308", "month": "abril de 2024"},
                    {"code": "309"},
                    "invalid_item",
                ],
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands": _FakeResponse(
                status_code=200,
                payload=[
                    {"code": "1", "name": "Scania"},
                    {"code": "2", "name": "Caterpillar Trucks"},
                ],
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models": _FakeResponse(
                status_code=200,
                payload=[
                    {"code": "10", "name": "FH 540 Diesel"},
                    {"code": "11", "name": "FH 460"},
                ],
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models/10/years": _FakeResponse(
                status_code=200,
                payload=[
                    {"code": "2021-1", "name": "2021 Diesel"},
                    {"code": "2020-3", "name": "Ano 2020 Diesel"},
                    {"code": "X-0", "name": "Sem ano"},
                ],
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models/10/years/2021-1": _FakeResponse(
                status_code=200,
                payload={"price": "R$ 10.000,00"},
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models/10/years/2020-3": _FakeResponse(
                status_code=200,
                payload={"price": "R$ 5.432,10"},
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/2/models": _FakeResponse(
                status_code=200,
                payload=[{"code": "20", "name": "Caterpillar Model A"}],
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/2/models/20/years": _FakeResponse(
                status_code=200,
                payload=[{"code": "2020-9", "name": "Ano 2020 Diesel"}],
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/2/models/20/years/2020-9": _FakeResponse(
                status_code=200,
                payload={"price": "R$ 1.000,00"},
            ),
        }

        session = _SequencedFakeSession(behaviors=behaviors)

        with mock.patch.object(fipe_client_module.time, "sleep", return_value=None):
            client = FipeClientHttp(session=session, timeout_s=0.01)

            price_2021 = client.get_fipe_price(
                brand="Scania", model="FH 540 Diesel", manufacturing_year=2021
            )
            self.assertEqual(price_2021, Decimal("10000.00"))

            price_substring = client.get_fipe_price(
                brand="Caterpillar", model="Model", manufacturing_year=2020
            )
            self.assertEqual(price_substring, Decimal("1000.00"))

            price_substring_cached = client.get_fipe_price(
                brand="Caterpillar", model="Model", manufacturing_year=2020
            )
            self.assertEqual(price_substring_cached, Decimal("1000.00"))

            price_2020_substring_model = client.get_fipe_price(
                brand="Scania", model="540", manufacturing_year=2020
            )
            self.assertEqual(price_2020_substring_model, Decimal("5432.10"))

    def test_year_label_with_two_years_matches_second_year(self):
        """FIPE às vezes retorna '2023/2024 ...' — o ano do veículo pode ser o segundo."""
        base_url = fipe_client_module.FIPE_BASE_URL
        vehicle_type = fipe_client_module.FIPE_TRUCK_VEHICLE_TYPE

        behaviors = {
            rf"{re.escape(base_url)}/references": _FakeResponse(
                status_code=200,
                payload=[{"code": "308", "month": "abril de 2024"}],
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands": _FakeResponse(
                status_code=200,
                payload=[{"code": "1", "name": "Scania"}],
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models": _FakeResponse(
                status_code=200,
                payload=[{"code": "10", "name": "FH 540 Diesel"}],
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models/10/years": _FakeResponse(
                status_code=200,
                payload=[
                    {"code": "2024-1", "name": "2023/2024 Diesel"},
                ],
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models/10/years/2024-1": _FakeResponse(
                status_code=200,
                payload={"price": "R$ 99.999,00"},
            ),
        }

        with mock.patch.object(fipe_client_module.time, "sleep", return_value=None):
            client = FipeClientHttp(
                session=_SequencedFakeSession(behaviors=behaviors), timeout_s=0.01
            )
            price = client.get_fipe_price(
                brand="Scania", model="FH 540 Diesel", manufacturing_year=2024
            )
            self.assertEqual(price, Decimal("99999.00"))

    def test_partial_model_name_tries_next_variant_when_year_missing(self):
        """
        Modelo parcial pode casar várias variantes na FIPE; a primeira pode não ter o ano.
        Deve-se tentar a próxima variante compatível (ex.: Mercedes Actros 2651 E6 vs E5).
        """
        base_url = fipe_client_module.FIPE_BASE_URL
        vehicle_type = fipe_client_module.FIPE_TRUCK_VEHICLE_TYPE

        behaviors = {
            rf"{re.escape(base_url)}/references": _FakeResponse(
                status_code=200,
                payload=[{"code": "308", "month": "abril de 2024"}],
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands": _FakeResponse(
                status_code=200,
                payload=[{"code": "1", "name": "Mercedes-Benz"}],
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models": _FakeResponse(
                status_code=200,
                payload=[
                    {"code": "10", "name": "Actros 2651 LS 6x4 (diesel)(E6)"},
                    {"code": "11", "name": "Actros 2651 LS 6x4 2p (diesel)(E5)"},
                ],
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models/10/years": _FakeResponse(
                status_code=200,
                payload=[{"code": "2024-3", "name": "2024"}],
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models/11/years": _FakeResponse(
                status_code=200,
                payload=[{"code": "2021-3", "name": "2021"}],
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models/11/years/2021-3": _FakeResponse(
                status_code=200,
                payload={"price": "R$ 50.000,00"},
            ),
        }

        with mock.patch.object(fipe_client_module.time, "sleep", return_value=None):
            client = FipeClientHttp(
                session=_SequencedFakeSession(behaviors=behaviors), timeout_s=0.01
            )
            price = client.get_fipe_price(
                brand="Mercedes-Benz", model="Actros 2651", manufacturing_year=2021
            )
            self.assertEqual(price, Decimal("50000.00"))

    def test_reference_invalid_payload_raises(self):
        base_url = fipe_client_module.FIPE_BASE_URL
        session = _SequencedFakeSession(
            behaviors={
                rf"{re.escape(base_url)}/references": _FakeResponse(status_code=200, payload={})
            }
        )
        with mock.patch.object(fipe_client_module.time, "sleep", return_value=None):
            client = FipeClientHttp(session=session, timeout_s=0.01)
            with self.assertRaises(InvalidFipeDataError):
                client.get_fipe_price(
                    brand="Scania", model="FH 540 Diesel", manufacturing_year=2020
                )

    def test_invalid_brand_model_year_raises(self):
        base_url = fipe_client_module.FIPE_BASE_URL
        vehicle_type = fipe_client_module.FIPE_TRUCK_VEHICLE_TYPE

        behaviors_brand = {
            rf"{re.escape(base_url)}/references": _FakeResponse(
                status_code=200, payload=[{"code": "308", "month": "abril de 2024"}]
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands": _FakeResponse(
                status_code=200, payload=[{"code": "1", "name": "Scania"}]
            ),
        }
        with mock.patch.object(fipe_client_module.time, "sleep", return_value=None):
            client = FipeClientHttp(
                session=_SequencedFakeSession(behaviors=behaviors_brand), timeout_s=0.01
            )
            with self.assertRaises(InvalidFipeDataError):
                client.get_fipe_price(
                    brand="Unknown Brand", model="FH 540 Diesel", manufacturing_year=2020
                )

        behaviors_model = {
            rf"{re.escape(base_url)}/references": _FakeResponse(
                status_code=200, payload=[{"code": "308", "month": "abril de 2024"}]
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands": _FakeResponse(
                status_code=200, payload=[{"code": "1", "name": "Scania"}]
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models": _FakeResponse(
                status_code=200, payload=[{"code": "10", "name": "FH 460"}]
            ),
        }
        with mock.patch.object(fipe_client_module.time, "sleep", return_value=None):
            client = FipeClientHttp(
                session=_SequencedFakeSession(behaviors=behaviors_model), timeout_s=0.01
            )
            with self.assertRaises(InvalidFipeDataError):
                client.get_fipe_price(
                    brand="Scania", model="FH 540 Diesel", manufacturing_year=2020
                )

        behaviors_year = {
            rf"{re.escape(base_url)}/references": _FakeResponse(
                status_code=200, payload=[{"code": "308", "month": "abril de 2024"}]
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands": _FakeResponse(
                status_code=200, payload=[{"code": "1", "name": "Scania"}]
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models": _FakeResponse(
                status_code=200, payload=[{"code": "10", "name": "FH 540 Diesel"}]
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models/10/years": _FakeResponse(
                status_code=200, payload=[{"code": "X-0", "name": "Sem ano"}]
            ),
        }
        with mock.patch.object(fipe_client_module.time, "sleep", return_value=None):
            client = FipeClientHttp(
                session=_SequencedFakeSession(behaviors=behaviors_year), timeout_s=0.01
            )
            with self.assertRaises(InvalidFipeDataError):
                client.get_fipe_price(
                    brand="Scania", model="FH 540 Diesel", manufacturing_year=2020
                )

    def test_unexpected_types_and_http_errors(self):
        base_url = fipe_client_module.FIPE_BASE_URL
        vehicle_type = fipe_client_module.FIPE_TRUCK_VEHICLE_TYPE
        url_references = f"{base_url}/references"

        with mock.patch.object(fipe_client_module.time, "sleep", return_value=None):
            client = FipeClientHttp(
                session=_SequencedFakeSession(behaviors={}, raise_on={url_references}),
                timeout_s=0.01,
            )
            with self.assertRaises(InvalidFipeDataError):
                client.get_fipe_price(
                    brand="Scania", model="FH 540 Diesel", manufacturing_year=2020
                )

        with mock.patch.object(fipe_client_module.time, "sleep", return_value=None):
            client = FipeClientHttp(
                session=_SequencedFakeSession(
                    behaviors={
                        rf"{re.escape(url_references)}": _FakeResponse(status_code=500, payload={})
                    }
                ),
                timeout_s=0.01,
            )
            with self.assertRaises(InvalidFipeDataError):
                client.get_fipe_price(
                    brand="Scania", model="FH 540 Diesel", manufacturing_year=2020
                )

        with mock.patch.object(fipe_client_module.time, "sleep", return_value=None):
            client = FipeClientHttp(
                session=_SequencedFakeSession(
                    behaviors={
                        rf"{re.escape(url_references)}": _FakeResponse(
                            status_code=200, payload={}, json_exc=ValueError("json inválido")
                        )
                    }
                ),
                timeout_s=0.01,
            )
            with self.assertRaises(InvalidFipeDataError):
                client.get_fipe_price(
                    brand="Scania", model="FH 540 Diesel", manufacturing_year=2020
                )

        behaviors_brands_bad = {
            rf"{re.escape(base_url)}/references": _FakeResponse(
                status_code=200, payload=[{"code": "308", "month": "abril de 2024"}]
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands": _FakeResponse(
                status_code=200, payload={}
            ),
        }
        with mock.patch.object(fipe_client_module.time, "sleep", return_value=None):
            client = FipeClientHttp(
                session=_SequencedFakeSession(behaviors=behaviors_brands_bad), timeout_s=0.01
            )
            with self.assertRaises(InvalidFipeDataError):
                client.get_fipe_price(
                    brand="Scania", model="FH 540 Diesel", manufacturing_year=2020
                )

        behaviors_models_bad = {
            rf"{re.escape(base_url)}/references": _FakeResponse(
                status_code=200, payload=[{"code": "308", "month": "abril de 2024"}]
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands": _FakeResponse(
                status_code=200, payload=[{"code": "1", "name": "Scania"}]
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models": _FakeResponse(
                status_code=200, payload={}
            ),
        }
        with mock.patch.object(fipe_client_module.time, "sleep", return_value=None):
            client = FipeClientHttp(
                session=_SequencedFakeSession(behaviors=behaviors_models_bad), timeout_s=0.01
            )
            with self.assertRaises(InvalidFipeDataError):
                client.get_fipe_price(
                    brand="Scania", model="FH 540 Diesel", manufacturing_year=2020
                )

        behaviors_years_bad = {
            rf"{re.escape(base_url)}/references": _FakeResponse(
                status_code=200, payload=[{"code": "308", "month": "abril de 2024"}]
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands": _FakeResponse(
                status_code=200, payload=[{"code": "1", "name": "Scania"}]
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models": _FakeResponse(
                status_code=200, payload=[{"code": "10", "name": "FH 540 Diesel"}]
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models/10/years": _FakeResponse(
                status_code=200, payload={}
            ),
        }
        with mock.patch.object(fipe_client_module.time, "sleep", return_value=None):
            client = FipeClientHttp(
                session=_SequencedFakeSession(behaviors=behaviors_years_bad), timeout_s=0.01
            )
            with self.assertRaises(InvalidFipeDataError):
                client.get_fipe_price(
                    brand="Scania", model="FH 540 Diesel", manufacturing_year=2020
                )

    def test_final_price_missing_or_invalid_format(self):
        base_url = fipe_client_module.FIPE_BASE_URL
        vehicle_type = fipe_client_module.FIPE_TRUCK_VEHICLE_TYPE

        behaviors_missing_price = {
            rf"{re.escape(base_url)}/references": _FakeResponse(
                status_code=200, payload=[{"code": "308", "month": "abril de 2024"}]
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands": _FakeResponse(
                status_code=200, payload=[{"code": "1", "name": "Scania"}]
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models": _FakeResponse(
                status_code=200, payload=[{"code": "10", "name": "FH 540 Diesel"}]
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models/10/years": _FakeResponse(
                status_code=200, payload=[{"code": "2020-3", "name": "2020 Diesel"}]
            ),
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models/10/years/2020-3": _FakeResponse(
                status_code=200, payload={}
            ),
        }
        with mock.patch.object(fipe_client_module.time, "sleep", return_value=None):
            client = FipeClientHttp(
                session=_SequencedFakeSession(behaviors=behaviors_missing_price), timeout_s=0.01
            )
            with self.assertRaises(InvalidFipeDataError):
                client.get_fipe_price(
                    brand="Scania", model="FH 540 Diesel", manufacturing_year=2020
                )

        behaviors_price_non_str = dict(behaviors_missing_price)
        behaviors_price_non_str[
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models/10/years/2020-3"
        ] = _FakeResponse(
            status_code=200,
            payload={"price": 123},
        )
        with mock.patch.object(fipe_client_module.time, "sleep", return_value=None):
            client = FipeClientHttp(
                session=_SequencedFakeSession(behaviors=behaviors_price_non_str), timeout_s=0.01
            )
            with self.assertRaises(InvalidFipeDataError):
                client.get_fipe_price(
                    brand="Scania", model="FH 540 Diesel", manufacturing_year=2020
                )

        behaviors_price_bad = dict(behaviors_missing_price)
        behaviors_price_bad[
            rf"{re.escape(base_url)}/{vehicle_type}/brands/1/models/10/years/2020-3"
        ] = _FakeResponse(
            status_code=200,
            payload={"price": "R$ abc"},
        )
        with mock.patch.object(fipe_client_module.time, "sleep", return_value=None):
            client = FipeClientHttp(
                session=_SequencedFakeSession(behaviors=behaviors_price_bad), timeout_s=0.01
            )
            with self.assertRaises(InvalidFipeDataError):
                client.get_fipe_price(
                    brand="Scania", model="FH 540 Diesel", manufacturing_year=2020
                )

    def test_unmapped_endpoint_raises_assertion_error_from_fake_session(self):
        base_url = fipe_client_module.FIPE_BASE_URL

        behaviors = {
            rf"{re.escape(base_url)}/references": _FakeResponse(
                status_code=200,
                payload=[{"code": "308", "month": "abril de 2024"}],
            )
        }
        session = _SequencedFakeSession(behaviors=behaviors)

        with mock.patch.object(fipe_client_module.time, "sleep", return_value=None):
            client = FipeClientHttp(session=session, timeout_s=0.01)
            with self.assertRaises(AssertionError):
                client.get_fipe_price(
                    brand="Scania", model="FH 540 Diesel", manufacturing_year=2020
                )
