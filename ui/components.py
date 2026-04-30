"""Reusable Streamlit rendering helpers."""

from __future__ import annotations

import re

import streamlit as st


def render_agent_step(title: str, payload: object, notes: str | None = None) -> None:
    with st.expander(title, expanded=True):
        if payload is None:
            st.info("No data produced in this step.")
        else:
            st.json(payload)
        if notes:
            st.caption(notes)


def render_supplier_table(ranked_quotes: list[dict]) -> None:
    st.subheader("Supplier comparison")
    if not ranked_quotes:
        st.warning("No supplier quotes to display.")
        return
    st.dataframe(ranked_quotes, use_container_width=True)


def render_purchase_order(po: dict) -> None:
    st.subheader("Purchase order preview")
    summary_cols = st.columns(4)
    summary_cols[0].metric("PO number", str(po.get("po_number", "n/a")))
    summary_cols[1].metric("Supplier", str(po.get("supplier", "n/a")))
    summary_cols[2].metric("Status", str(po.get("status", "n/a")))
    summary_cols[3].metric("Total EUR", _format_eur(float(po.get("total_eur", 0.0))))

    line_items = po.get("line_items", [])
    if line_items:
        st.markdown("**Line items**")
        st.dataframe(line_items, use_container_width=True)

    justification = str(po.get("justification", "")).strip()
    approval_memo = str(po.get("approval_memo", "")).strip()

    left, right = st.columns(2)
    with left:
        with st.container(border=True):
            st.markdown("**Purchase order justification**")
            _render_structured_bullets(justification)
    with right:
        with st.container(border=True):
            st.markdown("**Procurement approval memo**")
            _render_structured_bullets(approval_memo)


def render_errors(errors: list[str]) -> None:
    if not errors:
        return
    st.divider()
    st.subheader("Errors")
    for error in errors:
        st.error(error)


def _render_structured_bullets(text: str) -> None:
    bullets = [_emphasize_key_info(entry) for entry in _to_bullets(text)]
    st.markdown("\n".join(f"- {entry}" for entry in bullets))


def _to_bullets(text: str) -> list[str]:
    raw = (text or "").replace("\r", "").strip()
    if not raw:
        return ["Not available."]

    chunks: list[str] = []
    for line in raw.split("\n"):
        for part in line.split("|"):
            cleaned = part.strip()
            if cleaned:
                chunks.append(cleaned)

    if len(chunks) <= 2:
        expanded: list[str] = []
        for chunk in chunks:
            expanded.extend(
                sentence.strip()
                for sentence in re.split(r"(?<=[.!?])\s+", chunk)
                if sentence.strip()
            )
        if expanded:
            chunks = expanded

    bullets: list[str] = []
    for chunk in chunks:
        cleaned = re.sub(r"^\s*[-*]\s*", "", chunk)
        cleaned = re.sub(r"^\s*\d+[\)\.\:]\s*", "", cleaned)
        cleaned = cleaned.strip()
        if cleaned:
            bullets.append(cleaned)

    return bullets[:12] if bullets else ["Not available."]


def _emphasize_key_info(text: str) -> str:
    emphasized = text

    # Highlight important key/value segments first.
    key_value_pattern = re.compile(
        r"(?i)\b(item|supplier|unit price|unit_price_eur|quantity|qty|total value|total amount|total eur|"
        r"budget status|recommendation|subject|status)\b\s*:\s*([^|]+)"
    )

    def key_value_repl(match: re.Match) -> str:
        key = match.group(1).strip()
        value = match.group(2).strip()
        return f"**{key}:** **{value}**"

    emphasized = key_value_pattern.sub(key_value_repl, emphasized)

    # Highlight EUR amounts and common quantity expressions.
    emphasized = re.sub(
        r"(?i)\bEUR\s*\d[\d,]*(?:\.\d+)?\b",
        lambda m: f"**{m.group(0)}**",
        emphasized,
    )
    emphasized = re.sub(
        r"€\s*\d[\d,]*(?:\.\d+)?",
        lambda m: f"**{m.group(0)}**",
        emphasized,
    )
    emphasized = re.sub(
        r"(?i)\b\d+\s*(?:units?|laptops?|desks?|cables?)\b",
        lambda m: f"**{m.group(0)}**",
        emphasized,
    )
    emphasized = re.sub(
        r"(?i)\b(approve|approved|reject|rejected)\b",
        lambda m: f"**{m.group(0)}**",
        emphasized,
    )

    return emphasized


def _format_eur(amount: float) -> str:
    return f"EUR {amount:,.2f}"
