"""Session state helpers for Streamlit app."""

from __future__ import annotations

import streamlit as st


def init_session_state() -> None:
    if "result" not in st.session_state:
        st.session_state.result = None
