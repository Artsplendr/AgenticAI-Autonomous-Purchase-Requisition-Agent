"""ERP MCP server stub."""

from mcp_servers.erp.client import ERPMCPClient


def run() -> None:
    client = ERPMCPClient()
    print(f"ERP MCP ready with {len(client.get_item_catalog())} items")


if __name__ == '__main__':
    run()
