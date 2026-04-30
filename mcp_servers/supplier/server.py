"""Supplier MCP server stub with provider-based backend routing."""

from mcp_servers.supplier.client import SupplierMCPClient


def run() -> None:
    client = SupplierMCPClient()
    count = len(client.search_suppliers("laptop", 1))
    print(
        "Supplier MCP ready "
        f"(mode={client.provider_mode}, format={client.api_response_format}, base_url={client.api_base_url or 'n/a'}) "
        f"with {count} laptop supplier(s)"
    )


if __name__ == "__main__":
    run()
