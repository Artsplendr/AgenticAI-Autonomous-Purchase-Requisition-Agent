"""Supplier agent: generate synthetic supplier options from request category."""

from __future__ import annotations

from agents.base_agent import BaseAgent
from graph.state import RequisitionState
from models.supplier import Quote
from tools.synthetic_suppliers import generate_synthetic_quotes


class SupplierAgent(BaseAgent):
    async def run(self, state: RequisitionState) -> RequisitionState:
        state["current_step"] = "supplier"
        parsed = state.get("parsed_requisition")
        items = parsed.items if parsed else []
        if not items:
            state["errors"].append("SupplierAgent: no parsed items to source.")
            return state

        target_name = items[0].name.lower()
        quantity = int(items[0].quantity)
        quotes = generate_synthetic_quotes(item_name=target_name, quantity=quantity)
        state["supplier_quotes"] = [Quote.model_validate(quote.model_dump()) for quote in quotes]
        state["supplier_search_notes"] = (
            f"Generated {len(quotes)} synthetic supplier quote(s) from item category '{target_name}'."
        )
        if not quotes:
            state["errors"].append("SupplierAgent: no supplier quotes available for request.")
        return state
