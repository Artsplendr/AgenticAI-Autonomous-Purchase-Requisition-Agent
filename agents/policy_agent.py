"""Policy agent: LLM-driven compliance reasoning over policy snippets."""

from __future__ import annotations

import re

from agents.base_agent import BaseAgent
from graph.state import RequisitionState
from models.policy import PolicyCheck
from tools.llm_client import LLMClient, LLMError
from tools.rag_retriever import retrieve_policy


class PolicyAgent(BaseAgent):
    async def run(self, state: RequisitionState) -> RequisitionState:
        state["current_step"] = "policy"
        parsed = state.get("parsed_requisition")
        if not parsed:
            state["errors"].append("PolicyAgent: missing parsed requisition.")
            state["policy_check"] = PolicyCheck(compliant=False, rules=[], hard_block=True, missing_fields=["parsed_requisition"])
            state["policy_snippet_count"] = 0
            return state

        item = parsed.items[0]
        snippets = retrieve_policy(f"{item.name} {parsed.department} {parsed.urgency}")
        state["policy_snippet_count"] = len(snippets)
        missing_fields = _detect_missing_mandatory_fields(parsed.notes or "", item.name, int(item.quantity or 0), parsed.department)
        compliant_by_required_fields = len(missing_fields) == 0

        llm = LLMClient()
        try:
            response = llm.complete_json(
                task_name="policy_analysis",
                system_prompt=(
                    "You are a procurement policy compliance specialist. "
                    "Return strict JSON with keys: compliant (bool), rules (list[str]), rationale (str), "
                    "hard_block (bool), missing_fields (list[str]). "
                    "Use the provided policy snippets as mandatory evidence and cite concrete rules in 'rules'. "
                    "Treat missing mandatory requisition fields as non-compliant but NOT hard block (hard_block=false). "
                    "Use hard_block=true only for prohibited/restricted categories that must halt processing. "
                    "Supplier is not required at policy stage and should not be treated as missing."
                ),
                user_prompt=(
                    "Evaluate compliance for this requisition against policy snippets.\n"
                    f"Requisition: item={item.name}, quantity={item.quantity}, department={parsed.department}, urgency={parsed.urgency}\n"
                    f"Detected mandatory fields missing (pre-check): {missing_fields}\n"
                    f"Policy snippets: {snippets}\n"
                    "Respond with JSON only."
                ),
            )
            rules = [str(entry) for entry in response.get("rules", [])]
            # Mandatory-field completeness is enforced by deterministic pre-check.
            # LLM output may still mention concerns in rationale/rules.
            llm_compliant = bool(response.get("compliant", False))
            state["policy_check"] = PolicyCheck(
                compliant=llm_compliant and compliant_by_required_fields,
                rules=rules,
                hard_block=bool(response.get("hard_block", False)),
                missing_fields=missing_fields,
            )
            state["applicable_rules"] = rules
            state["policy_rationale"] = str(response.get("rationale", "")).strip()
        except LLMError as exc:
            state["policy_check"] = PolicyCheck(compliant=False, rules=[], hard_block=True, missing_fields=["policy_llm_unavailable"])
            state["applicable_rules"] = []
            state["policy_rationale"] = None
            state["errors"].append(f"PolicyAgent LLM failed: {exc}")
        return state


def _detect_missing_mandatory_fields(
    request_text: str,
    item_name: str,
    quantity: int,
    department: str,
) -> list[str]:
    lower = request_text.lower()
    business_reason_terms = (
        "for ",
        "because ",
        "due to ",
        "to support",
        "onboarding",
        "delivery",
        "compliance",
        "project",
        "inventory",
    )
    has_business_justification = any(term in lower for term in business_reason_terms)
    has_quantity = re.search(r"\b\d+\b", request_text) is not None and quantity > 0

    missing_fields: list[str] = []
    if not item_name:
        missing_fields.append("item_name")
    if not has_quantity:
        missing_fields.append("quantity")
    if department == "unknown":
        missing_fields.append("department")
    if not has_business_justification:
        missing_fields.append("business_justification")
    return missing_fields
