"""Optimizer agent: LLM-driven supplier comparison and recommendation."""

from __future__ import annotations

from agents.base_agent import BaseAgent
from graph.state import RequisitionState
from tools.llm_client import LLMClient, LLMError


class OptimizerAgent(BaseAgent):
    async def run(self, state: RequisitionState) -> RequisitionState:
        state["current_step"] = "optimizer"
        quotes = state.get("supplier_quotes") or []
        if not quotes:
            state["ranked_quotes"] = []
            state["best_quote"] = None
            state["optimizer_rationale"] = "No quotes were available to rank."
            return state

        config = state.get("config") or {}
        price_weight = float(config.get("price_weight", 0.5))
        delivery_weight = float(config.get("delivery_weight", 0.3))
        reliability_weight = float(config.get("reliability_weight", 0.2))

        llm = LLMClient()
        quote_payload = [
            {
                "supplier_id": quote.supplier_id,
                "supplier_name": quote.supplier_name,
                "unit_price_eur": quote.unit_price_eur,
                "delivery_days": quote.delivery_days,
                "reliability": quote.reliability,
                "categories": quote.categories,
            }
            for quote in quotes
        ]

        try:
            response = llm.complete_json(
                task_name="supplier_optimization",
                system_prompt=(
                    "You are a procurement optimizer. "
                    "Return strict JSON with keys: ranked_suppliers (list of {supplier_id, score}), "
                    "best_supplier_id (str), rationale (str)."
                ),
                user_prompt=(
                    f"Supplier quotes: {quote_payload}\n"
                    f"Weights: price={price_weight}, delivery={delivery_weight}, reliability={reliability_weight}\n"
                    "Rank suppliers and pick one best supplier. Score range must be 0..1. JSON only."
                ),
            )
            score_by_supplier = {
                str(entry.get("supplier_id")): float(entry.get("score", 0.0))
                for entry in response.get("ranked_suppliers", [])
                if isinstance(entry, dict)
            }
            ordered_ids = [entry.get("supplier_id") for entry in response.get("ranked_suppliers", []) if isinstance(entry, dict)]

            ranked = []
            for supplier_id in ordered_ids:
                match = next((quote for quote in quotes if quote.supplier_id == supplier_id), None)
                if match:
                    ranked.append(match.model_copy(update={"score": round(score_by_supplier.get(supplier_id, 0.0), 3)}))

            best_supplier_id = str(response.get("best_supplier_id", ""))
            best_quote = next((quote for quote in ranked if quote.supplier_id == best_supplier_id), None)
            if not ranked or not best_quote:
                raise LLMError("LLM ranking did not return valid supplier ids from available quotes.")

            state["ranked_quotes"] = ranked
            state["best_quote"] = best_quote
            state["optimizer_rationale"] = str(response.get("rationale", "")).strip()
        except LLMError as exc:
            state["ranked_quotes"] = []
            state["best_quote"] = None
            state["optimizer_rationale"] = None
            state["errors"].append(f"OptimizerAgent LLM failed: {exc}")
        return state
