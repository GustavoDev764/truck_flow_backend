from __future__ import annotations

import re
import time
import unicodedata
from dataclasses import dataclass
from decimal import Decimal
from typing import Any

import requests

from apps.trucks.domain.exceptions import InvalidFipeDataError
from apps.trucks.domain.repositories import FipeClient
from config.env import env

FIPE_BASE_URL = env.FIPE_BASE_URL
FIPE_TRUCK_VEHICLE_TYPE = env.FIPE_TRUCK_VEHICLE_TYPE


FIPE_APP_URL_TEMPLATE = env.FIPE_APP_URL_TEMPLATE


def _normalize_text(value: str) -> str:

    value = unicodedata.normalize("NFKD", value)
    value = value.encode("ascii", "ignore").decode("ascii")
    value = value.strip().upper()
    value = re.sub(r"\s+", " ", value)
    return value


def _parse_brl_price(value: str) -> Decimal:

    if not isinstance(value, str):
        raise InvalidFipeDataError("Formato inesperado de valor FIPE.")

    cleaned = value.replace("R$", "").strip()
    cleaned = cleaned.replace(".", "").replace(",", ".")
    try:
        return Decimal(cleaned)
    except Exception as exc:
        raise InvalidFipeDataError("Não foi possível interpretar o valor FIPE.") from exc


@dataclass
class _FipeReference:
    code: str
    month: str


class FipeClientHttp(FipeClient):
    """
    Cliente HTTP para a FIPE (v2).

    Implementado na infra para isolar regras de integração do domínio.
    """

    def __init__(self, *, session: requests.Session | None = None, timeout_s: float = 10.0):
        self._session = session or requests.Session()
        self._timeout_s = timeout_s

        self._reference_code: str | None = None
        self._brands_cache: dict[str, list[dict[str, Any]]] = {}
        self._models_cache: dict[tuple[str, str], list[dict[str, Any]]] = {}
        self._years_cache: dict[tuple[str, str], list[dict[str, Any]]] = {}

    def get_fipe_price(self, *, brand: str, model: str, manufacturing_year: int) -> Decimal:
        reference_code = self._get_reference_code()
        brand_id = self._find_brand_id(reference_code, brand)
        model_id, year_id = self._resolve_model_and_year_ids(
            reference_code, brand_id, model, manufacturing_year
        )

        payload = self._get_json(
            f"{FIPE_BASE_URL}/{FIPE_TRUCK_VEHICLE_TYPE}/brands/{brand_id}/models/{model_id}/years/{year_id}",
            params={"reference": reference_code},
        )

        price_value = payload.get("price")
        if price_value is None:
            raise InvalidFipeDataError("A FIPE não retornou o campo 'price'.")

        return _parse_brl_price(price_value)

    def get_brands(self) -> list[dict[str, Any]]:
        """Lista marcas disponíveis na tabela FIPE (para catálogo/select)."""
        ref = self._get_reference_code()
        return self._get_brands(ref)

    def get_models(self, brand_id: str) -> list[dict[str, Any]]:
        """Lista modelos da marca (para catálogo/select)."""
        ref = self._get_reference_code()
        return self._get_models(ref, brand_id)

    def get_years(self, brand_id: str, model_id: str) -> list[dict[str, int]]:
        """
        Lista anos disponíveis para o modelo (para catálogo/select).
        Retorna lista de {year: int} com anos únicos, ordenados decrescente.
        """
        ref = self._get_reference_code()
        raw = self._get_years(ref, brand_id, model_id)
        seen: set[int] = set()
        years: list[int] = []
        for item in raw:
            for y in _candidate_years_from_fipe_year_item(item):
                if y not in seen:
                    seen.add(y)
                    years.append(y)
        years.sort(reverse=True)
        return [{"year": y} for y in years]

    def _get_reference_code(self) -> str:
        if self._reference_code is not None:
            return self._reference_code

        payload = self._get_json(f"{FIPE_BASE_URL}/references")
        if not isinstance(payload, list) or not payload:
            raise InvalidFipeDataError("Não foi possível obter referência da FIPE.")

        references: list[_FipeReference] = []
        for item in payload:
            if isinstance(item, dict) and "code" in item and "month" in item:
                references.append(_FipeReference(code=str(item["code"]), month=str(item["month"])))

        self._reference_code = max(references, key=lambda r: int(r.code)).code
        return self._reference_code

    def _find_brand_id(self, reference_code: str, brand: str) -> str:
        brands = self._get_brands(reference_code)
        target = _normalize_text(brand)
        substring_match: str | None = None

        for b in brands:
            name = _normalize_text(str(b.get("name", "")))
            if target == name:
                return str(b["code"])
            if substring_match is None and (target in name or name in target):
                substring_match = str(b["code"])

        if substring_match is not None:
            return substring_match
        raise InvalidFipeDataError("Marca inválida para a tabela FIPE.")

    def _get_brands(self, reference_code: str) -> list[dict[str, Any]]:
        if reference_code in self._brands_cache:
            return self._brands_cache[reference_code]

        payload = self._get_json(
            f"{FIPE_BASE_URL}/{FIPE_TRUCK_VEHICLE_TYPE}/brands",
            params={"reference": reference_code},
        )
        if not isinstance(payload, list):
            raise InvalidFipeDataError("Resposta inesperada da FIPE para marcas.")

        self._brands_cache[reference_code] = payload
        return payload

    def _resolve_model_and_year_ids(
        self,
        reference_code: str,
        brand_id: str,
        model: str,
        manufacturing_year: int,
    ) -> tuple[str, str]:
        """
        Resolve modelo + código do ano na FIPE.

        Quando o usuário informa um modelo parcial (ex.: \"Actros 2651\"), a FIPE
        pode ter várias variantes (E5/E6, cabines, eixos). A primeira variante na
        lista nem sempre inclui o ano desejado — então tentamos, na ordem da API,
        cada candidato até achar um que possua o `manufacturing_year`.
        """
        models = self._get_models(reference_code, brand_id)
        target = _normalize_text(model)

        exact = [m for m in models if _normalize_text(str(m.get("name", ""))) == target]
        exact_codes = {str(m["code"]) for m in exact}
        substring = [
            m
            for m in models
            if str(m["code"]) not in exact_codes
            and (
                target in _normalize_text(str(m.get("name", "")))
                or _normalize_text(str(m.get("name", ""))) in target
            )
        ]
        to_try = exact + substring
        if not to_try:
            raise InvalidFipeDataError("Modelo inválido para a tabela FIPE.")

        for m in to_try:
            mid = str(m["code"])
            year_id = self._try_find_year_id(reference_code, brand_id, mid, manufacturing_year)
            if year_id is not None:
                return mid, year_id

        raise InvalidFipeDataError("Ano de fabricação inválido para a tabela FIPE.")

    def _try_find_year_id(
        self,
        reference_code: str,
        brand_id: str,
        model_id: str,
        manufacturing_year: int,
    ) -> str | None:
        years = self._get_years(reference_code, brand_id, model_id)
        target_year = int(manufacturing_year)
        for y in years:
            candidates = _candidate_years_from_fipe_year_item(y)
            if target_year in candidates:
                return str(y["code"])
        return None

    def _get_models(self, reference_code: str, brand_id: str) -> list[dict[str, Any]]:
        key = (reference_code, brand_id)
        if key in self._models_cache:
            return self._models_cache[key]

        payload = self._get_json(
            f"{FIPE_BASE_URL}/{FIPE_TRUCK_VEHICLE_TYPE}/brands/{brand_id}/models",
            params={"reference": reference_code},
        )
        if not isinstance(payload, list):
            raise InvalidFipeDataError("Resposta inesperada da FIPE para modelos.")

        self._models_cache[key] = payload
        return payload

    def _get_years(self, reference_code: str, brand_id: str, model_id: str) -> list[dict[str, Any]]:
        key = (reference_code, f"{brand_id}:{model_id}")
        if key in self._years_cache:
            return self._years_cache[key]

        payload = self._get_json(
            f"{FIPE_BASE_URL}/{FIPE_TRUCK_VEHICLE_TYPE}/brands/{brand_id}/models/{model_id}/years",
            params={"reference": reference_code},
        )
        if not isinstance(payload, list):
            raise InvalidFipeDataError("Resposta inesperada da FIPE para anos.")

        self._years_cache[key] = payload
        return payload

    def _get_json(self, url: str, *, params: dict[str, Any] | None = None) -> Any:
        try:
            time.sleep(0.05)
            resp = self._session.get(url, params=params, timeout=self._timeout_s)
        except requests.RequestException as exc:
            raise InvalidFipeDataError("Erro ao consultar a FIPE.") from exc

        if resp.status_code != 200:
            raise InvalidFipeDataError(f"FIPE retornou status HTTP {resp.status_code}.")

        try:
            return resp.json()
        except Exception as exc:
            raise InvalidFipeDataError("Resposta inválida da FIPE (JSON).") from exc


def _extract_year_from_fipe_year_name(name: str) -> int | None:

    match = re.match(r"^\s*(\d{4})", str(name))
    if not match:
        match = re.search(r"(\d{4})", str(name))
        if not match:
            return None
    return int(match.group(1))


def _extract_year_from_fipe_year_code(code: str) -> int | None:
    """
    O campo `code` da FIPE costuma ser `AAAA-N` (ano + variante combustível).
    Alguns proxies retornam só o ano no prefixo.
    """
    raw = str(code).strip()
    if not raw:
        return None
    head = raw.split("-", 1)[0]
    if head.isdigit() and len(head) == 4:
        y = int(head)
        if 1900 <= y <= 2100:
            return y
    return None


def _years_in_fipe_year_label(name: str) -> list[int]:
    """
    Rótulos como '2023/2024 Diesel' ou 'Ano 2020 Diesel' podem ter mais de um ano.
    Consideramos apenas anos plausíveis 1900–2100 via padrão 19xx/20xx.
    """
    text = str(name)
    found: list[int] = []
    for m in re.finditer(r"\b(19\d{2}|20\d{2})\b", text):
        y = int(m.group(1))
        if 1900 <= y <= 2100:
            found.append(y)
    return found


def _candidate_years_from_fipe_year_item(item: dict[str, Any]) -> set[int]:
    """Todos os anos que a entrada da FIPE pode representar (code + name)."""
    out: set[int] = set()
    code_y = _extract_year_from_fipe_year_code(str(item.get("code", "")))
    if code_y is not None:
        out.add(code_y)
    name = str(item.get("name", ""))
    for y in _years_in_fipe_year_label(name):
        out.add(y)
    if not out:
        legacy = _extract_year_from_fipe_year_name(name)
        if legacy is not None and 1900 <= legacy <= 2100:
            out.add(legacy)
    return out
