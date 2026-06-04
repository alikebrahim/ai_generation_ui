"""Shared Streamlit styling for the app shell."""

from __future__ import annotations

import streamlit as st

APP_STYLE = """
<style>
    .block-container {
        padding-top: 1.35rem;
        padding-bottom: 2.5rem;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 0.35rem;
    }

    .stTabs [data-baseweb="tab"] {
        border-radius: 0.75rem 0.75rem 0 0;
        padding: 0.45rem 0.85rem;
    }

    .stButton > button {
        width: 100%;
    }

    div[data-testid="stStatusWidget"] {
        border-radius: 0.9rem;
    }

    div[data-testid="stMetric"] {
        border-radius: 0.75rem;
    }

    .ai-shell-note {
        color: rgba(49, 51, 63, 0.75);
        font-size: 0.92rem;
        margin-top: -0.25rem;
    }

    .ai-shell-card {
        border: 1px solid rgba(49, 51, 63, 0.12);
        border-radius: 0.9rem;
        padding: 1rem 1rem 0.85rem 1rem;
        background: rgba(255, 255, 255, 0.03);
    }

    .ai-prediction-preview-anchor {
        display: block;
        height: 0;
        margin: 0;
        padding: 0;
    }

    div[data-testid="stVerticalBlockBorderWrapper"]:has(.ai-prediction-preview-anchor) {
        border: 2px solid rgba(255, 75, 75, 0.72);
        border-radius: 1rem;
        box-shadow: 0 0 0 1px rgba(255, 75, 75, 0.12);
        min-height: 18rem;
    }

    .ai-gallery-thumb {
        display: block;
        position: relative;
        overflow: hidden;
        border-radius: 0.75rem;
        border: 1px solid rgba(49, 51, 63, 0.14);
        text-decoration: none;
    }

    .ai-gallery-thumb img {
        display: block;
        width: 100%;
        height: auto;
    }

    .ai-gallery-thumb span {
        position: absolute;
        right: 0.45rem;
        bottom: 0.45rem;
        border-radius: 999px;
        padding: 0.15rem 0.5rem;
        background: rgba(0, 0, 0, 0.68);
        color: white;
        font-size: 0.75rem;
    }
</style>
"""


def inject_app_style() -> None:
    """Inject a lightweight CSS layer for layout reliability and spacing."""
    st.markdown(APP_STYLE, unsafe_allow_html=True)
