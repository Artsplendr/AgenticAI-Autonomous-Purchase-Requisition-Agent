"""Policy MCP server stub."""

from mcp_servers.policy.client import PolicyMCPClient


def run() -> None:
    client = PolicyMCPClient()
    snippets = client.retrieve_policy('laptop approval')
    print(f"Policy MCP ready with {len(snippets)} snippet(s)")


if __name__ == '__main__':
    run()
