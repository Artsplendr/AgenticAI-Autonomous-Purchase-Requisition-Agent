"""Minimal async workflow object compatible with LangGraph-style ainvoke."""

from __future__ import annotations

from graph.edges import route_after_optimizer, route_after_policy
from graph.nodes import (
    run_approval,
    run_interpreter,
    run_optimizer,
    run_policy,
    run_supplier,
)
from graph.state import RequisitionState


class RequisitionWorkflow:
    async def ainvoke(self, state: RequisitionState) -> RequisitionState:
        state = await run_interpreter(state)
        if state.get("errors"):
            return state

        state = await run_policy(state)
        if route_after_policy(state) == "hard_block":
            return state

        state = await run_supplier(state)
        state = await run_optimizer(state)
        if route_after_optimizer(state) != "proceed":
            return state

        state = await run_approval(state)
        return state


workflow = RequisitionWorkflow()
