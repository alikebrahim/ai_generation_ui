"""Audio-specific generation form (music vs speech layouts)."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from src import utils as app_utils
from src.models_config import ModelConfig
from src.pricing import calculate_cost
from src.ui.form_utils import normalize_file_kwargs
from src.ui.forms import friendly_label, render_param_widget
from src.ui.request_preview import render_request_preview


def _primary_text_params(model: ModelConfig) -> list[str]:
    order = ("lyrics", "text", "prompt")
    return [p for p in order if p in model.balanced_params]


def _estimate_audio_cost_label(model: ModelConfig, kwargs: dict) -> str:
    text_len = 0
    for key in ("lyrics", "text", "prompt"):
        val = kwargs.get(key)
        if isinstance(val, str):
            text_len += len(val)
    duration = kwargs.get("duration")
    if isinstance(duration, (int, float)) and duration > 0:
        cost = calculate_cost(
            model.replicate_id,
            0.0,
            output_duration=float(duration),
            text_length=text_len,
        )
    elif text_len > 0:
        cost = calculate_cost(
            model.replicate_id, 0.0, text_length=text_len
        )
    else:
        cost = calculate_cost(model.replicate_id, 0.0, text_length=0)
    if cost <= 0 and text_len == 0:
        return model.pricing_notes or "Cost shown after generation"
    return app_utils.format_cost(cost)


def render_audio_generation_form(
    model: ModelConfig,
    preview_renderer: Callable[[], None] | None = None,
) -> dict | None:
    """Render music/speech generation workspace.

    Primary creative input (lyrics/text/prompt) lives in the left column above
    the result preview for visual consistency with video/3D (left = workspace).
    Right column is secondary settings + generate only.
    """
    st.subheader(f"Generate with {model.display_name}")

    kwargs: dict = {}
    preview_col, controls_col = st.columns([1.9, 1.6], vertical_alignment="top")

    with preview_col:
        # Main creative input (moved to left for space + consistency)
        with st.container(border=True):
            st.markdown("#### Main input")
            for param in _primary_text_params(model):
                label = friendly_label(param, model)
                help_text = (model.param_help or {}).get(param, "")
                height = 140 if param == "lyrics" else 110
                kwargs[param] = st.text_area(
                    label,
                    height=height,
                    help=help_text or None,
                    key=f"audio_{model.name}_{param}",
                )

        # Result preview / status area (anchor for red border CSS parity)
        with st.container(border=True):
            st.markdown(
                "<span class='ai-prediction-preview-anchor'></span>",
                unsafe_allow_html=True,
            )
            if preview_renderer is not None:
                preview_renderer()
            else:
                st.info("Run a generation and the audio preview will appear here.")

    controls_box = controls_col.container(border=True)

    with controls_box:
        st.markdown("#### Main settings")
        skip = set(_primary_text_params(model))
        for param_name in model.balanced_params:
            if param_name in skip:
                continue
            value = render_param_widget(model, param_name)
            if value is not None or param_name == "seed":
                kwargs[param_name] = value

        if model.advanced_params:
            with st.expander("More settings (optional)", expanded=False):
                for param_name in model.advanced_params:
                    value = render_param_widget(model, param_name, advanced=True)
                    if value is not None:
                        kwargs[param_name] = value

        st.caption(f"Estimated cost: {_estimate_audio_cost_label(model, kwargs)}")
        render_request_preview(model, kwargs)

        generate_clicked = st.button(
            "Generate Audio",
            type="primary",
            key=f"btn_{model.name}",
            use_container_width=True,
        )

    if not generate_clicked:
        return None

    for group in getattr(model, "required_one_of", []):
        satisfied = any(
            isinstance(kwargs.get(p), str) and kwargs.get(p, "").strip()
            for p in group
        )
        if not satisfied:
            labels = " or ".join(friendly_label(p, model) for p in group)
            st.error(f"Please provide {labels}.")
            return None

    if model.requires_text:
        primary = _primary_text_params(model)
        if primary and not str(kwargs.get(primary[0], "")).strip():
            st.error(f"Please enter {friendly_label(primary[0], model).lower()}.")
            return None

    return normalize_file_kwargs(model, kwargs)
