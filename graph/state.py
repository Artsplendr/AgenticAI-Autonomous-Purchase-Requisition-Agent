"""Typed state object passed through the requisition workflow."""

from __future__ import annotations

from typing import Any, TypedDict

from models.policy import PolicyCheck
from models.purchase_order import PurchaseOrder
from models.requisition import ParsedRequisition
from models.supplier import Quote


class RequisitionState(TypedDict):
    raw_request: str
    parsed_requisition: ParsedRequisition | None
    interpreter_notes: str | None
    policy_check: PolicyCheck | None
    policy_snippet_count: int
    policy_rationale: str | None
    applicable_rules: list[str] | None
    supplier_quotes: list[Quote] | None
    supplier_search_notes: str | None
    ranked_quotes: list[Quote] | None
    best_quote: Quote | None
    optimizer_rationale: str | None
    budget_result: dict[str, Any] | None
    approval_needed: bool | None
    approval_status: str | None
    approved_by: str | None
    approval_memo: str | None
    purchase_order: PurchaseOrder | None
    config: dict[str, Any]
    errors: list[str]
    current_step: str
