"""Routing helpers used by the lightweight workflow implementation."""

from __future__ import annotations

from graph.state import RequisitionState


def route_after_policy(state: RequisitionState) -> str:
    policy_check = state.get("policy_check")
    hard_block = bool(policy_check.hard_block) if policy_check else True
    return "hard_block" if hard_block else "proceed"


def route_after_optimizer(state: RequisitionState) -> str:
    return "proceed" if state.get("best_quote") else "no_quote"
