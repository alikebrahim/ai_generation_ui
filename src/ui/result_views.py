"""Result display rendering for generated videos and 3D models."""

from __future__ import annotations

from pathlib import Path
from urllib.parse import quote

import streamlit as st

from src import utils as app_utils

format_duration = app_utils.format_duration
format_cost = app_utils.format_cost
friendly_error_message = app_utils.friendly_error_message
technical_error_detail = app_utils.technical_error_detail


def _safe_caption_path(value: object) -> str | None:
    if not value or not isinstance(value, str):
        return None
    path = Path(value)
    return str(path) if path.exists() and path.is_file() else None


def _result_error(result: dict) -> str:
    error = result.get("error") or "Generation failed"
    return friendly_error_message(error)


def _render_failure_debug(result: dict) -> None:
    """Optional expander with prediction link and raw provider error."""
    pred_id = result.get("prediction_id") or ""
    pred_url = result.get("prediction_url") or ""
    raw = result.get("error_detail") or technical_error_detail(result.get("error"))
    if not (pred_id or pred_url or raw):
        return
    with st.expander("Technical details (for troubleshooting)"):
        if pred_url:
            st.markdown(f"[Open job on Replicate]({pred_url})")
        elif pred_id:
            st.caption(f"Prediction id: `{pred_id}`")
        if raw:
            st.code(str(raw), language=None)


def _render_common_failure(result: dict, kind: str) -> None:
    st.error(f"{kind.title()} generation failed")
    st.write(_result_error(result))
    job_url = result.get("prediction_url") or ""
    if job_url:
        st.link_button("Open job on Replicate", job_url, use_container_width=False)
    _render_failure_debug(result)
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


def render_image_result(result: dict) -> None:
    """Render an image generation result or failure message."""
    if not result.get("success", False):
        _render_common_failure(result, "image")
        return

    url = result.get("url") or ""
    local_path = _safe_caption_path(result.get("local_file_path"))
    display_src = local_path or url
    extra_urls = result.get("urls") or []

    st.caption(f"Completed in {format_duration(result.get('predict_time', 0))}")
    if display_src:
        st.image(display_src, use_container_width=True)
    for idx, extra in enumerate(extra_urls[1:], start=2):
        st.caption(f"Output {idx}")
        st.image(extra, use_container_width=True)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if url:
            st.link_button("Open / download image", url, use_container_width=True)
        elif local_path:
            st.caption(f"Local file: `{local_path}`")
    with col_b:
        st.metric("Predict time", format_duration(result.get("predict_time", 0)))
    with col_c:
        st.metric("Estimated cost", format_cost(result.get("estimated_cost", 0)))

    if result.get("prediction_url"):
        st.caption(f"Replicate prediction: {result['prediction_url']}")
    if local_path:
        st.caption(f"Saved locally — `{local_path}`")
    else:
        st.caption("Output URLs are hosted by Replicate and may expire after ~1 hour.")


def render_audio_result(result: dict) -> None:
    """Render an audio generation result or failure message."""
    if not result.get("success", False):
        _render_common_failure(result, "audio")
        return

    url = result.get("url") or ""
    local_path = _safe_caption_path(result.get("local_file_path"))
    play_src = local_path or url

    st.caption(f"Completed in {format_duration(result.get('predict_time', 0))}")
    if play_src:
        st.audio(play_src)

    col_a, col_b, col_c = st.columns(3)
    with col_a:
        if url:
            st.link_button("Open / download audio", url, use_container_width=True)
        elif local_path:
            st.caption(f"Local file: `{local_path}`")
    with col_b:
        st.metric("Predict time", format_duration(result.get("predict_time", 0)))
    with col_c:
        st.metric("Estimated cost", format_cost(result.get("estimated_cost", 0)))

    if result.get("prediction_url"):
        st.caption(f"Replicate prediction: {result['prediction_url']}")
    if local_path:
        st.caption(f"Saved locally — `{local_path}`")
    else:
        st.caption("Output URLs are hosted by Replicate and may expire after ~1 hour.")


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
