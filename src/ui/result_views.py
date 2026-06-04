"""Result display rendering for generated videos and 3D models."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

import streamlit as st

from src import utils as app_utils

format_duration = app_utils.format_duration
format_cost = app_utils.format_cost
friendly_error_message = app_utils.friendly_error_message


def _safe_caption_path(value: object) -> str | None:
    if not value or not isinstance(value, str):
        return None
    path = Path(value)
    return str(path) if path.exists() and path.is_file() else None


def _result_error(result: dict) -> str:
    error = result.get("error") or "Generation failed"
    return friendly_error_message(error)


def _render_common_failure(result: dict, kind: str) -> None:
    st.error(f"{kind.title()} generation failed")
    st.write(_result_error(result))
    if result.get("prediction_url"):
        st.caption(f"Replicate prediction: {result['prediction_url']}")
    local = _safe_caption_path(result.get("local_file_path"))
    if local:
        st.caption(f"Saved file still exists locally: {local}")


def render_video_result(result: dict) -> None:
    """Render a video generation result or failure message."""
    if not result.get("success", False):
        _render_common_failure(result, "video")
        return

    url = result.get("url") or ""
    st.caption(f"Completed in {format_duration(result['predict_time'])}")
    if url:
        st.video(url)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if url:
            st.link_button("Open / download video", url, use_container_width=True)
    with col_b:
        st.metric("Predict time", format_duration(result["predict_time"]))
    with col_c:
        st.metric("Estimated cost", format_cost(result.get("estimated_cost", 0)))

    if result.get("prediction_url"):
        st.caption(f"Replicate prediction: {result['prediction_url']}")
    if result.get("local_file_path"):
        st.caption(f"✅ Saved locally — `{result['local_file_path']}`")
    else:
        st.caption("Output URLs are hosted by Replicate and expire after about 1 hour.")


def render_3d_result(result: dict) -> None:
    """Render a 3D generation result or failure message."""
    if not result.get("success", False):
        _render_common_failure(result, "3D")
        return

    model_url = result.get("model_url") or result.get("mesh_url", "")
    preview_url = result.get("video_url", "")

    st.caption(f"Completed in {format_duration(result['predict_time'])}")

    if model_url:
        safe_url = quote(model_url, safe=":/?&=#%+-_.,~")
        viewer_html = f"""
        <model-viewer
            src="{safe_url}"
            alt="Generated 3D model"
            auto-rotate
            camera-controls
            style="width:100%; height:500px; background:#1a1a2e;
                   border-radius:0.85rem;">
        </model-viewer>
        <script type="module"
            src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.5.0/model-viewer.min.js">
        </script>
        """
        st.components.v1.html(viewer_html, height=520)

    if preview_url:
        st.caption("Preview animation")
        st.video(preview_url)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if model_url:
            st.link_button(
                "Open / download 3D model", model_url, use_container_width=True
            )
    with col_b:
        st.metric("Predict time", format_duration(result["predict_time"]))
    with col_c:
        st.metric("Estimated cost", format_cost(result.get("estimated_cost", 0)))

    if result.get("prediction_url"):
        st.caption(f"Replicate prediction: {result['prediction_url']}")
    if result.get("local_file_path"):
        st.caption(f"✅ Saved locally — `{result['local_file_path']}`")
    else:
        st.caption("Output URLs are hosted by Replicate and expire after about 1 hour.")
