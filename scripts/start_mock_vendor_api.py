"""Start the local mock vendor API for supplier MCP demos."""

from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from mcp_servers.supplier.mock_vendor_api import main


if __name__ == "__main__":
    main()
