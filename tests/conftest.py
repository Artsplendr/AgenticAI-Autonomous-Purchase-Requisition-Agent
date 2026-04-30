"""Pytest config to make project packages importable from tests."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))


@pytest.fixture(autouse=True)
def stub_llm_calls(monkeypatch):
    from tools.llm_client import LLMClient

    def _fake_complete_json(self, *, task_name: str, system_prompt: str, user_prompt: str):
        if task_name == "policy_analysis":
            return {
                "compliant": True,
                "rules": [
                    "procurement_policy: approved supplier policy applies.",
                    "approval_thresholds: manager approval threshold is enforced.",
                ],
                "rationale": "Policy check completed against synthetic company policy.",
                "hard_block": False,
                "missing_fields": [],
            }
        if task_name == "supplier_optimization":
            return {
                "ranked_suppliers": [
                    {"supplier_id": "lenovo-eu", "score": 0.72},
                    {"supplier_id": "dell-eu", "score": 0.68},
                ],
                "best_supplier_id": "lenovo-eu",
                "rationale": "Lenovo EU selected for strongest overall weighted score.",
            }
        if task_name == "approval_memo_and_po_justification":
            return {
                "approval_memo": (
                    "PROCUREMENT APPROVAL MEMO: Request for laptop procurement from approved supplier. "
                    "Recommendation: APPROVE for processing."
                ),
                "po_justification": (
                    "Purchase justified by onboarding demand, unit economics, and supplier reliability."
                ),
            }
        raise RuntimeError(f"Unexpected LLM task in tests: {task_name}")

    monkeypatch.setattr(LLMClient, "complete_json", _fake_complete_json)
