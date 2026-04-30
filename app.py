"""
app.py
------
Streamlit demo UI for the Autonomous Purchase Requisition Agent.
Run with: streamlit run app.py
"""

import asyncio
import re
import streamlit as st
from pydantic import BaseModel
from config.settings import settings
from graph.workflow import workflow
from graph.state import RequisitionState
from ui.session_state import init_session_state
from ui.components import (
    render_agent_step,
    render_supplier_table,
    render_purchase_order,
    render_errors,
)


def _to_jsonable(payload):
    if isinstance(payload, BaseModel):
        return payload.model_dump()
    if isinstance(payload, list):
        return [_to_jsonable(item) for item in payload]
    if isinstance(payload, dict):
        return {key: _to_jsonable(value) for key, value in payload.items()}
    return payload


def _mandatory_fields_status(request_text: str) -> dict[str, bool]:
    lower = request_text.lower()
    department_terms = {
        "engineering",
        "operations",
        "finance",
        "hr",
        "marketing",
        "sales",
        "procurement",
        "it",
    }
    item_terms = {"laptop", "desk", "chair", "monitor", "keyboard", "mouse", "usb", "cable"}
    has_quantity = re.search(r"\b\d+\b", request_text) is not None
    has_department = any(term in lower for term in department_terms)
    has_item = any(term in lower for term in item_terms)
    has_business_justification = any(
        token in lower for token in (" for ", " because ", " due to ", "to support", "for the", "for a")
    )
    return {
        "item_name": has_item,
        "quantity": has_quantity,
        "department": has_department,
        "business_justification": has_business_justification,
    }

st.set_page_config(
    page_title="Purchase Requisition Agent",
    page_icon="🧾",
    layout="wide",
)

st.markdown(
    """
    <style>
    /* Hide top-right deploy/menu controls for business-facing UI */
    [data-testid="stAppDeployButton"] {display: none;}
    [data-testid="stToolbar"] {display: none;}

    /* Reduce top margin/padding by roughly 50% */
    .block-container {
        padding-top: 1.5rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("🧾 Autonomous Purchase Requisition Agent")
st.caption("From plain-language request → validated, compliant, approved PO")

init_session_state()

if "request_text" not in st.session_state:
    st.session_state.request_text = ""
if "request_example" not in st.session_state:
    st.session_state.request_example = "Choose an example..."
if "_last_request_example" not in st.session_state:
    st.session_state._last_request_example = ""

# ── Sidebar ──────────────────────────────────────────────────────────────────
with st.sidebar:
    examples = [
        "We need 10 laptops for the new engineering team joining next month to support onboarding and sprint delivery.",
        "Order 5 standing desks for the Berlin office to meet ergonomic compliance requirements for new hires.",
        "Buy 100 USB-C cables for IT support inventory to reduce device setup delays during onboarding.",
    ]
    example_choice = st.selectbox(
        "Default examples",
        ["Choose an example..."] + examples,
        key="request_example",
    )
    if example_choice != "Choose an example..." and example_choice != st.session_state._last_request_example:
        st.session_state.request_text = example_choice
        st.session_state._last_request_example = example_choice

    request = st.text_area(
        "Purchase Request",
        placeholder='e.g. "We need 20 laptops for the new engineering team"',
        height=80,
        key="request_text",
    )
    mandatory_status = _mandatory_fields_status(request)

    with st.container(border=True):
        st.markdown("**Mandatory Fields Check**")
        st.write(f"{'✅' if mandatory_status['item_name'] else '⚠️'} Item name")
        st.write(f"{'✅' if mandatory_status['quantity'] else '⚠️'} Quantity")
        st.write(f"{'✅' if mandatory_status['department'] else '⚠️'} Department")
        st.write(f"{'✅' if mandatory_status['business_justification'] else '⚠️'} Business justification")
        if all(mandatory_status.values()):
            st.success("All mandatory fields detected in request text.")
        else:
            missing = [name for name, ok in mandatory_status.items() if not ok]
            st.info("Missing fields to add in request text: " + ", ".join(missing))

    col1, col2 = st.columns([2, 1])
    with col1:
        run_btn = st.button("▶ Run Agent", type="primary", use_container_width=True)
    with col2:
        clear_btn = st.button("🗑 Clear", use_container_width=True)

    st.divider()
    st.header("⚙️ Settings")
    st.slider("Auto-approval threshold (€)", 1000, 50000, 5000, 1000,
              key="approval_threshold")
    st.slider("Price weight",       0.0, 1.0, 0.5, 0.1, key="price_weight")
    st.slider("Delivery weight",    0.0, 1.0, 0.3, 0.1, key="delivery_weight")
    st.slider("Reliability weight", 0.0, 1.0, 0.2, 0.1, key="reliability_weight")

if clear_btn:
    st.session_state.result = None
    st.session_state.request_text = ""
    st.session_state.request_example = "Choose an example..."
    st.session_state._last_request_example = ""
    st.rerun()

# ── Run pipeline ──────────────────────────────────────────────────────────────
if run_btn and request.strip():
    initial: RequisitionState = {
        "raw_request":           request,
        "parsed_requisition":    None,
        "interpreter_notes":     None,
        "policy_check":          None,
        "policy_snippet_count":  0,
        "policy_rationale":      None,
        "applicable_rules":      None,
        "supplier_quotes":       None,
        "supplier_search_notes": None,
        "ranked_quotes":         None,
        "best_quote":            None,
        "optimizer_rationale":   None,
        "budget_result":         None,
        "approval_needed":       None,
        "approval_status":       None,
        "approved_by":           None,
        "approval_memo":         None,
        "purchase_order":        None,
        "config": {
            "approval_threshold": st.session_state.get("approval_threshold", 5000),
            "price_weight": st.session_state.get("price_weight", 0.5),
            "delivery_weight": st.session_state.get("delivery_weight", 0.3),
            "reliability_weight": st.session_state.get("reliability_weight", 0.2),
        },
        "errors":                [],
        "current_step":          "start",
    }

    with st.spinner("🤖 Running agent pipeline..."):
        result = asyncio.run(workflow.ainvoke(initial))
        st.session_state.result = result

# ── Display results ───────────────────────────────────────────────────────────
if st.session_state.get("result"):
    r = st.session_state.result
    policy_check_json = _to_jsonable(r.get("policy_check")) or {}
    missing_fields = policy_check_json.get("missing_fields", []) if isinstance(policy_check_json, dict) else []
    if missing_fields:
        st.warning(
            "Mandatory fields missing (PO blocked until fixed): " + ", ".join(missing_fields)
        )

    if r.get("ranked_quotes"):
        render_supplier_table(_to_jsonable(r["ranked_quotes"]))

    if r.get("purchase_order"):
        st.divider()
        render_purchase_order(_to_jsonable(r["purchase_order"]))

    st.divider()
    with st.expander("🔍 Agent Trace", expanded=False):
        render_agent_step("1️⃣ Interpreter Agent", _to_jsonable(r.get("parsed_requisition")), r.get("interpreter_notes"))
        render_agent_step(
            "2️⃣ Policy Agent",
            _to_jsonable(r.get("policy_check")),
            (
                f"Policy snippets retrieved: {r.get('policy_snippet_count', 0)}"
                f" | Missing mandatory fields: {', '.join(missing_fields) if missing_fields else 'none'}"
                f" | {r.get('policy_rationale') or ''}"
            ),
        )
        render_agent_step("3️⃣ Supplier Agent",    {"quotes_found": len(r.get("supplier_quotes") or [])}, r.get("supplier_search_notes"))
        render_agent_step("4️⃣ Optimizer Agent",   _to_jsonable(r.get("best_quote")),         r.get("optimizer_rationale"))
        render_agent_step(
            "5️⃣ Approval Agent",
            _to_jsonable(r.get("budget_result")),
            f"Status: {r.get('approval_status')} | Memo: {r.get('approval_memo') or 'n/a'}",
        )

    if r.get("errors"):
        render_errors(r["errors"])
