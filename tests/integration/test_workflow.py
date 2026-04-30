import asyncio

from graph.workflow import workflow


def test_workflow_generates_po_payload():
    state = {
        'raw_request': 'Order 5 standing desks for operations',
        'parsed_requisition': None,
        'interpreter_notes': None,
        'policy_check': None,
        'policy_snippet_count': 0,
        'policy_rationale': None,
        'applicable_rules': None,
        'supplier_quotes': None,
        'supplier_search_notes': None,
        'ranked_quotes': None,
        'best_quote': None,
        'optimizer_rationale': None,
        'budget_result': None,
        'approval_needed': None,
        'approval_status': None,
        'approved_by': None,
        'approval_memo': None,
        'purchase_order': None,
        'config': {
            'approval_threshold': 5000,
            'price_weight': 0.5,
            'delivery_weight': 0.3,
            'reliability_weight': 0.2,
        },
        'errors': [],
        'current_step': 'start',
    }
    result = asyncio.run(workflow.ainvoke(state))
    assert 'purchase_order' in result
