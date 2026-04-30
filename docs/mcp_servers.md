# MCP Servers (Auxiliary)

The repository includes local MCP-style stubs under `mcp_servers/`:

- `erp`
- `supplier`
- `policy`
- `budget`
- `approval`

Each server exposes a `run()` entry and lightweight handlers for experimentation.

## Current Runtime Setup

The default Streamlit workflow currently does **not** depend on supplier MCP provider modes.
Instead, `SupplierAgent` generates synthetic supplier quotes directly from request category and quantity.

The MCP supplier client/server code remains in the repo as optional integration assets for future extension.

## Optional MCP supplier experimentation

If you want to experiment with supplier MCP integration assets, see:

- `mcp_servers/supplier/client.py`
- `mcp_servers/supplier/providers.py`
- `mcp_servers/supplier/mock_vendor_api.py` (sample local API with built-in payload)
