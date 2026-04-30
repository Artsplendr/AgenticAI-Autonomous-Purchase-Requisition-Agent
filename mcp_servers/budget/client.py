"""Budget MCP client stub."""

from pathlib import Path
import json


class BudgetMCPClient:
    def __init__(self) -> None:
        self.mock_file = Path(__file__).parents[2] / 'data' / 'mock' / 'budget.json'
        self.default_budget = {
            "engineering": 45000.0,
            "operations": 30000.0,
            "finance": 25000.0,
        }

    def get_budget_balance(self, cost_center: str) -> float:
        if self.mock_file.exists():
            data = json.loads(self.mock_file.read_text())
        else:
            data = self.default_budget
        return float(data.get(cost_center, 0.0))
