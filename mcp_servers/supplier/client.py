"""Supplier MCP client using pluggable data providers."""

from __future__ import annotations

from pathlib import Path

from mcp_servers.supplier.providers import (
    HttpSupplierProvider,
    MockSupplierProvider,
    SupplierProvider,
    SupplierProviderError,
    build_response_mapper,
)
from models.supplier import Supplier


class SupplierMCPClient:
    def __init__(
        self,
        provider_mode: str | None = None,
        api_base_url: str | None = None,
        api_key: str | None = None,
        timeout_s: float | None = None,
        api_response_format: str | None = None,
    ) -> None:
        self.mock_file = Path(__file__).parents[2] / "data" / "mock" / "suppliers.json"
        self.provider_mode = (provider_mode or "mock").lower()
        self.api_base_url = api_base_url or ""
        self.api_key = api_key or ""
        self.timeout_s = timeout_s if timeout_s is not None else 8.0
        self.api_response_format = api_response_format or "generic"

    def search_suppliers(self, category: str, quantity: int) -> list[Supplier]:
        if self.provider_mode == "mock":
            return self._mock_provider().search_suppliers(category, quantity)
        if self.provider_mode == "api":
            return self._api_provider().search_suppliers(category, quantity)
        if self.provider_mode == "auto":
            return self._search_with_auto_fallback(category, quantity)
        raise ValueError(f"Unsupported supplier provider mode: {self.provider_mode}")

    def _search_with_auto_fallback(self, category: str, quantity: int) -> list[Supplier]:
        if self.api_base_url:
            try:
                api_results = self._api_provider().search_suppliers(category, quantity)
                if api_results:
                    return api_results
            except SupplierProviderError:
                # Fallback to built-in demo supplier provider when API is unavailable.
                pass
        return self._mock_provider().search_suppliers(category, quantity)

    def _mock_provider(self) -> SupplierProvider:
        return MockSupplierProvider(self.mock_file)

    def _api_provider(self) -> SupplierProvider:
        return HttpSupplierProvider(
            base_url=self.api_base_url,
            api_key=self.api_key,
            timeout_s=float(self.timeout_s),
            response_mapper=build_response_mapper(self.api_response_format),
        )
