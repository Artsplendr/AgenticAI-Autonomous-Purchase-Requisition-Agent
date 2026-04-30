"""Provider adapters for supplier MCP backend integrations."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Protocol
from urllib import error, parse, request

from models.supplier import Supplier


class SupplierProviderError(RuntimeError):
    """Raised when a provider cannot fetch supplier data."""


class SupplierResponseMapper(Protocol):
    def map_payload(self, payload: object) -> list[Supplier]:
        """Map provider-specific payload into normalized Supplier models."""


class SupplierProvider(Protocol):
    def search_suppliers(self, category: str, quantity: int) -> list[Supplier]:
        """Return normalized suppliers for a category and quantity."""


def demo_supplier_catalog() -> list[dict]:
    """Small built-in supplier catalog for MCP demo fallbacks."""
    return [
        {
            "id": "dell-eu",
            "name": "Dell EU",
            "categories": ["laptop", "monitor", "it-hardware"],
            "min_order_qty": 1,
            "unit_price_eur": 920.0,
            "delivery_days": 5,
            "reliability": 0.91,
        },
        {
            "id": "lenovo-eu",
            "name": "Lenovo EU",
            "categories": ["laptop", "it-hardware"],
            "min_order_qty": 1,
            "unit_price_eur": 880.0,
            "delivery_days": 7,
            "reliability": 0.87,
        },
        {
            "id": "ergofurn-eu",
            "name": "ErgoFurn EU",
            "categories": ["desk", "chair", "office-furniture"],
            "min_order_qty": 2,
            "unit_price_eur": 310.0,
            "delivery_days": 10,
            "reliability": 0.89,
        },
    ]


class MockSupplierProvider:
    def __init__(self, mock_file: Path) -> None:
        self.mock_file = mock_file

    def search_suppliers(self, category: str, quantity: int) -> list[Supplier]:
        if self.mock_file.exists():
            raw = json.loads(self.mock_file.read_text())
        else:
            raw = demo_supplier_catalog()
        suppliers = [Supplier.model_validate(item) for item in raw]
        category_lower = category.lower()
        return [
            supplier
            for supplier in suppliers
            if category_lower in [entry.lower() for entry in supplier.categories]
            and supplier.min_order_qty <= quantity
        ]


class GenericSupplierResponseMapper:
    """Fallback mapper that supports a few common generic shapes."""

    def map_payload(self, payload: object) -> list[Supplier]:
        raw_items = self._extract_items(payload)
        return [Supplier.model_validate(self._normalize_item(item)) for item in raw_items]

    @staticmethod
    def _extract_items(payload: object) -> list[dict]:
        if isinstance(payload, list):
            return [item for item in payload if isinstance(item, dict)]
        if isinstance(payload, dict):
            for key in ("suppliers", "results", "data", "items"):
                value = payload.get(key)
                if isinstance(value, list):
                    return [item for item in value if isinstance(item, dict)]
        return []

    @staticmethod
    def _normalize_item(item: dict) -> dict:
        categories = item.get("categories") or item.get("category") or []
        if isinstance(categories, str):
            categories = [categories]
        return {
            "id": item.get("id") or item.get("supplier_id") or item.get("vendor_id") or "unknown-id",
            "name": item.get("name") or item.get("supplier_name") or item.get("vendor_name") or "Unknown Supplier",
            "categories": categories,
            "min_order_qty": int(item.get("min_order_qty", item.get("minimum_order", 1))),
            "unit_price_eur": float(item.get("unit_price_eur", item.get("price", 0.0))),
            "delivery_days": int(item.get("delivery_days", item.get("eta_days", 7))),
            "reliability": float(item.get("reliability", item.get("rating", 0.7))),
        }


class AcmeVendorResponseMapper:
    """Concrete mapper for Acme Supplier API v1 payload format."""

    def map_payload(self, payload: object) -> list[Supplier]:
        if not isinstance(payload, dict):
            return []
        results = payload.get("results", [])
        if not isinstance(results, list):
            return []
        normalized: list[Supplier] = []
        for row in results:
            if not isinstance(row, dict):
                continue
            normalized.append(
                Supplier.model_validate(
                    {
                        "id": row.get("vendorCode", "unknown-id"),
                        "name": row.get("displayName", "Unknown Supplier"),
                        "categories": self._categories_from_row(row),
                        "min_order_qty": int(row.get("minimumOrder", 1)),
                        "unit_price_eur": float(row.get("pricing", {}).get("unitEur", 0.0)),
                        "delivery_days": int(row.get("fulfillment", {}).get("leadTimeDays", 7)),
                        "reliability": float(row.get("quality", {}).get("reliabilityScore", 0.7)),
                    }
                )
            )
        return normalized

    @staticmethod
    def _categories_from_row(row: dict) -> list[str]:
        categories = row.get("catalogTags") or row.get("category") or []
        if isinstance(categories, str):
            return [categories]
        if isinstance(categories, list):
            return [str(entry) for entry in categories]
        return []


def build_response_mapper(api_format: str) -> SupplierResponseMapper:
    key = (api_format or "generic").lower()
    if key == "acme_v1":
        return AcmeVendorResponseMapper()
    return GenericSupplierResponseMapper()


class HttpSupplierProvider:
    def __init__(
        self,
        base_url: str,
        api_key: str | None = None,
        timeout_s: float = 8.0,
        response_mapper: SupplierResponseMapper | None = None,
    ) -> None:
        self.base_url = base_url.rstrip("/")
        self.api_key = api_key
        self.timeout_s = timeout_s
        self.response_mapper = response_mapper or GenericSupplierResponseMapper()

    def search_suppliers(self, category: str, quantity: int) -> list[Supplier]:
        if not self.base_url:
            return []
        query = parse.urlencode({"category": category, "quantity": quantity})
        url = f"{self.base_url}/suppliers/search?{query}"
        headers = {"Accept": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"

        req = request.Request(url=url, method="GET", headers=headers)
        try:
            with request.urlopen(req, timeout=self.timeout_s) as response:
                body = response.read().decode("utf-8")
        except (error.HTTPError, error.URLError, TimeoutError) as exc:
            raise SupplierProviderError(f"Supplier API request failed: {exc}") from exc

        payload = json.loads(body)
        suppliers = self.response_mapper.map_payload(payload)
        category_lower = category.lower()
        return [
            supplier
            for supplier in suppliers
            if category_lower in [entry.lower() for entry in supplier.categories]
            and supplier.min_order_qty <= quantity
        ]
