"""Shared generation status panel helpers for Video and 3D tabs."""

from __future__ import annotations

from collections.abc import Callable
from time import monotonic
from typing import Any

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from src.generation_progress import ProgressUpdater, typical_duration_hint
from src.generation_service import get_generation_service
from src.models_config import ModelConfig
from src.utils import friendly_error_message

PreviewHandles = dict[str, DeltaGenerator]


def render_idle_preview_message(model_type: str) -> str:
    """Copy shown before the first generation in the preview panel."""
    hint = typical_duration_hint(model_type)
    key = model_type.lower()
    label = {"3d": "3D", "audio": "Audio", "image": "Image"}.get(key, "Video")
    return (
        "Run a generation and live status plus the final preview will stay open "
        f"here. {label} jobs take {hint}."
    )


def build_preview_panel(
    *,
    result_key: str,
    model_type: str,
    render_result: Callable[[dict], None],
) -> tuple[PreviewHandles, Callable[[], None]]:
    """Create preview panel placeholders and a renderer callback for forms."""
    handles: PreviewHandles = {}

    def render_preview_panel() -> None:
        st.markdown("#### Prediction status / preview")
        handles["status"] = st.empty()
        handles["progress"] = st.empty()
        result_area = st.empty()
        handles["result"] = result_area
        latest = st.session_state.get(result_key)
        if latest:
            with result_area.container():
                render_result(latest)
        else:
            handles["status"].info(render_idle_preview_message(model_type))

    return handles, render_preview_panel


def render_generation_started(status_line: DeltaGenerator, model: ModelConfig) -> None:
    """Initial in-flight message while the job is being created."""
    hint = typical_duration_hint(model.model_type)
    status_line.info(
        f"Generating with **{model.display_name}** — status updates below. "
        f"Most jobs take {hint}."
    )


def run_model_generation(
    *,
    model: ModelConfig,
    handles: PreviewHandles,
    result_key: str,
    kwargs: dict[str, Any],
    render_result: Callable[[dict], None],
    use_spinner: bool = False,
    spinner_message: str = "",
) -> None:
    """Run generation with shared progress UI and outcome handling."""
    status_line = handles.get("status") or st.empty()
    progress_line = handles.get("progress") or st.empty()
    result_area = handles.get("result") or st.empty()

    render_generation_started(status_line, model)
    start_time = monotonic()
    progress_callback = ProgressUpdater(
        progress_line,
        model_type=model.model_type,
        start_time=start_time,
    )

    try:
        gen_kwargs = dict(kwargs)
        gen_kwargs["progress_callback"] = progress_callback

        def _execute() -> dict:
            return get_generation_service().generate(
                model.name,
                model.model_type,
                **gen_kwargs,
            )

        if use_spinner and spinner_message:
            with st.spinner(spinner_message):
                result = _execute()
        else:
            result = _execute()

        st.session_state[result_key] = result
        progress_line.empty()

        if result.get("success"):
            status_line.success("Generation complete.")
            with result_area.container():
                render_result(result)
        else:
            status_line.error(
                friendly_error_message(result.get("error", "Generation failed"))
            )
            with result_area.container():
                render_result(result)
    except Exception as exc:
        progress_line.empty()
        result = {
            "success": False,
            "error": friendly_error_message(exc),
            "error_detail": str(exc),
            "predict_time": 0,
            "estimated_cost": 0,
        }
        st.session_state[result_key] = result
        status_line.error("Generation failed — see details below.")
        with result_area.container():
            render_result(result)
