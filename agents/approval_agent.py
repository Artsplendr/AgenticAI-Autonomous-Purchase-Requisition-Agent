"""Approval agent: budget check, approval decision, and PO payload."""

from __future__ import annotations

from datetime import datetime
import re

from agents.base_agent import BaseAgent
from graph.state import RequisitionState
from models.purchase_order import POLineItem, PurchaseOrder
from tools.llm_client import LLMClient, LLMError


class ApprovalAgent(BaseAgent):
    async def run(self, state: RequisitionState) -> RequisitionState:
        state["current_step"] = "approval"
        best_quote = state.get("best_quote")
        parsed = state.get("parsed_requisition")
        items = parsed.items if parsed else []
        quantity = int(items[0].quantity) if items else 1

        if not best_quote:
            state["approval_status"] = "not_started"
            state["errors"].append("ApprovalAgent: cannot approve without a selected quote.")
            return state

        policy_check = state.get("policy_check")
        missing_fields = policy_check.missing_fields if policy_check else []

        total_amount = round(float(best_quote.unit_price_eur) * quantity, 2)
        config = state.get("config") or {}
        threshold = float(config.get("approval_threshold", 5000))
        approval_needed = total_amount >= threshold

        state["budget_result"] = {
            "available": True,
            "check_status": "assumed_available",
            "note": "Current/remaining budget values are not shown in this demo.",
        }
        state["approval_needed"] = approval_needed
        status = "approved" if not approval_needed else "pending_human_review"
        state["approval_status"] = status
        state["approved_by"] = "auto-approval-engine" if not approval_needed else "manager@company.com"

        if missing_fields:
            state["approval_status"] = "blocked_missing_fields"
            state["approval_memo"] = (
                "PO generation blocked: mandatory requisition fields missing -> "
                + ", ".join(missing_fields)
            )
            state["purchase_order"] = None
            state["errors"].append(
                "ApprovalAgent: PO blocked until mandatory fields are completed: "
                + ", ".join(missing_fields)
            )
            return state

        llm = LLMClient()
        item_name = items[0].name if items else "item"
        try:
            response = llm.complete_json(
                task_name="approval_memo_and_po_justification",
                system_prompt=(
                    "You are a procurement approval specialist. "
                    "Return strict JSON with keys: approval_memo (str), po_justification (str)."
                ),
                user_prompt=(
                    f"Generate approval memo and PO justification.\n"
                    f"Item={item_name}, quantity={quantity}, supplier={best_quote.supplier_name}, "
                    f"unit_price_eur={best_quote.unit_price_eur}, total_eur={total_amount}\n"
                    f"Budget check status={state['budget_result']}\n"
                    f"Approval threshold={threshold}, approval_needed={approval_needed}\n"
                    "Do NOT include budget-related words, phrases, or figures. "
                    "Keep business tone concise and decision oriented. JSON only."
                ),
            )
            approval_memo = _strip_budget_language(str(response.get("approval_memo", "")).strip())
            po_justification = _strip_budget_language(str(response.get("po_justification", "")).strip())
            if not approval_memo or not po_justification:
                raise LLMError("LLM response missing approval_memo/po_justification after budget-language sanitization.")

            state["approval_memo"] = approval_memo
            state["purchase_order"] = PurchaseOrder(
                po_number=f"PO-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
                supplier=best_quote.supplier_name,
                status=state["approval_status"] or "pending_human_review",
                total_eur=total_amount,
                line_items=[
                    POLineItem(
                        item=item_name,
                        quantity=quantity,
                        unit_price_eur=best_quote.unit_price_eur,
                    )
                ],
                justification=po_justification,
                approval_memo=approval_memo,
            )
        except LLMError as exc:
            state["approval_memo"] = None
            state["purchase_order"] = None
            state["approval_status"] = "failed_llm_generation"
            state["errors"].append(f"ApprovalAgent LLM failed: {exc}")
        return state


def _strip_budget_language(text: str) -> str:
    if not text:
        return ""
    blocked = re.compile(
        r"(?i)\b(budget|remaining|reservation|funding|funds|balance|threshold|available budget|post-reservation)\b"
    )
    parts = re.split(r"(?<=[.!?])\s+|\n+", text)
    cleaned = [part.strip() for part in parts if part.strip() and not blocked.search(part)]
    return " ".join(cleaned).strip()
