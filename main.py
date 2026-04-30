"""CLI entry point to run one requisition through the workflow."""

from __future__ import annotations

import argparse
import asyncio
import json

from pydantic import BaseModel

from graph.workflow import workflow


def build_initial_state(request: str) -> dict:
    return {
        "raw_request": request,
        "parsed_requisition": None,
        "interpreter_notes": None,
        "policy_check": None,
        "policy_snippet_count": 0,
        "policy_rationale": None,
        "applicable_rules": None,
        "supplier_quotes": None,
        "supplier_search_notes": None,
        "ranked_quotes": None,
        "best_quote": None,
        "optimizer_rationale": None,
        "budget_result": None,
        "approval_needed": None,
        "approval_status": None,
        "approved_by": None,
        "approval_memo": None,
        "purchase_order": None,
        "config": {
            "approval_threshold": 5000,
            "price_weight": 0.5,
            "delivery_weight": 0.3,
            "reliability_weight": 0.2,
        },
        "errors": [],
        "current_step": "start",
    }


def _to_jsonable(payload):
    if isinstance(payload, BaseModel):
        return payload.model_dump()
    if isinstance(payload, list):
        return [_to_jsonable(item) for item in payload]
    if isinstance(payload, dict):
        return {key: _to_jsonable(value) for key, value in payload.items()}
    return payload


def main() -> None:
    parser = argparse.ArgumentParser(description='Run requisition workflow from CLI.')
    parser.add_argument('--request', required=True, help='Purchase request in plain language.')
    args = parser.parse_args()

    result = asyncio.run(workflow.ainvoke(build_initial_state(args.request)))
    print(json.dumps(_to_jsonable(result), indent=2))


if __name__ == '__main__':
    main()
