"""MCP server port mapping for local demo."""

from pydantic import BaseModel


class MCPConfig(BaseModel):
    erp_port: int = 8001
    supplier_port: int = 8002
    policy_port: int = 8003
    budget_port: int = 8004
    approval_port: int = 8005


mcp_config = MCPConfig()
