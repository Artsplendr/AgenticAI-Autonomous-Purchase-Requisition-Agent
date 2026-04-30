"""ERP MCP client stub."""

from pathlib import Path
import json


class ERPMCPClient:
    def __init__(self) -> None:
        self.mock_file = Path(__file__).parents[2] / 'data' / 'mock' / 'erp_items.json'
        self.default_items = [
            {"sku": "LAPTOP-001", "category": "laptop", "approved": True},
            {"sku": "DESK-001", "category": "desk", "approved": True},
            {"sku": "CABLE-USB-C-001", "category": "usb-c cable", "approved": True},
        ]

    def get_item_catalog(self) -> list[dict]:
        if self.mock_file.exists():
            return json.loads(self.mock_file.read_text())
        return self.default_items
