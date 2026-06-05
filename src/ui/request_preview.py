"""Dry-run request preview UI (no paid Replicate calls)."""

from __future__ import annotations

from typing import Any

import streamlit as st

from src.generation_service import get_generation_service
from src.models_config import ModelConfig
from src.ui.form_utils import normalize_file_kwargs
from src.validation import ValidationError, validate_params


def render_request_preview(
    model: ModelConfig,
    kwargs: dict[str, Any],
    *,
    preview_key_suffix: str = "",
) -> None:
    """Show request summary and payload when the user previews (no charge)."""
    session_key = f"request_preview_{model.name}{preview_key_suffix}"

    with st.expander("Preview request payload (advanced)", expanded=False):
        st.caption(
            "Checks your inputs and shows the Replicate payload that would be sent. "
            "This does not start a paid generation."
        )
        if st.button(
            "Update preview",
            key=f"preview_btn_{model.name}{preview_key_suffix}",
            use_container_width=True,
        ):
            validation_kwargs = normalize_file_kwargs(model, kwargs)
            try:
                validate_params(model, validation_kwargs)
            except ValidationError as exc:
                st.session_state[session_key] = {
                    "ok": False,
                    "validation_errors": str(exc).splitlines(),
                }
            else:
                st.session_state[session_key] = (
                    get_generation_service().prepare_generation_request(
                        model.name,
                        **kwargs,
                    )
                )

    preview = st.session_state.get(session_key)
    if not preview:
        return

    if not preview.get("ok"):
        st.error("Cannot preview this request yet:")
        for line in preview.get("validation_errors", []):
            st.markdown(f"- {line}")
        return

    for line in preview.get("summary_lines", []):
        st.markdown(line)

    endpoint = preview.get("endpoint", {})
    if endpoint.get("create_call"):
        st.code(endpoint["create_call"], language="text")

    schema_issues = preview.get("schema_diagnostics") or []
    if schema_issues:
        with st.expander("Schema diagnostics (developer)", expanded=False):
            for item in schema_issues:
                st.markdown(
                    f"- **{item['severity']}** `{item['code']}`: {item['message']}"
                )

    st.markdown("**Technical payload (copyable)**")
    st.code(preview.get("payload_json", "{}"), language="json")
