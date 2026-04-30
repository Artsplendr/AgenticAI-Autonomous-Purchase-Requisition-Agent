"""Shared base class for all workflow agents."""

from __future__ import annotations

from graph.state import RequisitionState


class BaseAgent:
    """Base contract for async agents that mutate state in place."""

    async def run(self, state: RequisitionState) -> RequisitionState:
        raise NotImplementedError("Agents must implement run().")
