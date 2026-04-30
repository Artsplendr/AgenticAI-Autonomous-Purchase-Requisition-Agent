"""Interpreter agent: parse free text into structured requisition fields."""

from __future__ import annotations

import re

from agents.base_agent import BaseAgent
from graph.state import RequisitionState
from models.requisition import Item, ParsedRequisition


class InterpreterAgent(BaseAgent):
    async def run(self, state: RequisitionState) -> RequisitionState:
        state["current_step"] = "interpreter"
        request = (state.get("raw_request") or "").strip()
        if not request:
            state["errors"].append("InterpreterAgent: empty request.")
            return state

        qty_match = re.search(r"\b(\d+)\b", request)
        quantity = int(qty_match.group(1)) if qty_match else 1
        lower = request.lower()

        item = "laptop" if "laptop" in lower else "desk" if "desk" in lower else "usb-c cable" if "usb" in lower else "office equipment"
        urgency = "high" if "urgent" in lower else "normal"
        department = "engineering" if "engineering" in lower else "operations" if "operations" in lower else "unknown"

        state["parsed_requisition"] = ParsedRequisition(
            items=[
                Item(
                    name=item,
                    quantity=quantity,
                    unit="unit",
                    estimated_unit_price_eur=None,
                )
            ],
            department=department,
            urgency=urgency,
            notes=request,
        )
        state["interpreter_notes"] = f"Parsed item '{item}' with quantity {quantity}."
        return state
