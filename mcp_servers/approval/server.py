"""Approval MCP server stub."""

from mcp_servers.approval.client import ApprovalMCPClient


def run() -> None:
    client = ApprovalMCPClient()
    result = client.send_approval_request('manager@company.com', 12000)
    print(f"Approval MCP ready. Email sent={result.get('sent')}")


if __name__ == '__main__':
    run()
