"""Budget MCP server stub."""

from mcp_servers.budget.client import BudgetMCPClient


def run() -> None:
    client = BudgetMCPClient()
    print(f"Budget MCP ready with engineering balance={client.get_budget_balance('engineering')}")


if __name__ == '__main__':
    run()
