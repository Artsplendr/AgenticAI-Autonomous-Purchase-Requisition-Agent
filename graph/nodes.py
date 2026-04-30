"""Workflow node wrappers around each agent."""

from __future__ import annotations

from agents.approval_agent import ApprovalAgent
from agents.interpreter_agent import InterpreterAgent
from agents.optimizer_agent import OptimizerAgent
from agents.policy_agent import PolicyAgent
from agents.supplier_agent import SupplierAgent
from graph.state import RequisitionState

_interpreter = InterpreterAgent()
_policy = PolicyAgent()
_supplier = SupplierAgent()
_optimizer = OptimizerAgent()
_approval = ApprovalAgent()


async def run_interpreter(state: RequisitionState) -> RequisitionState:
    return await _interpreter.run(state)


async def run_policy(state: RequisitionState) -> RequisitionState:
    return await _policy.run(state)


async def run_supplier(state: RequisitionState) -> RequisitionState:
    return await _supplier.run(state)


async def run_optimizer(state: RequisitionState) -> RequisitionState:
    return await _optimizer.run(state)


async def run_approval(state: RequisitionState) -> RequisitionState:
    return await _approval.run(state)
