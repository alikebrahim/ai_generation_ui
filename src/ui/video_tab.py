"""Video generation tab for Streamlit app."""

from __future__ import annotations

from time import monotonic

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from src import utils as app_utils
from src.generation_service import get_generation_service
from src.models_config import VIDEO_MODELS
from src.ui.forms import render_generation_form
from src.ui.result_views import render_video_result
from src.validation import validate_params

format_duration = app_utils.format_duration
friendly_error_message = app_utils.friendly_error_message


def render_video_tab() -> None:
    """Render the video generation tab."""
    st.header("Video Generation")
    st.caption(
        "Choose a model, tune the prompt, and keep the result in one focused panel."
    )

    video_idx = int(st.session_state.get("video_model", 0))
    if video_idx < 0 or video_idx >= len(VIDEO_MODELS):
        video_idx = 0
    model = VIDEO_MODELS[video_idx]
    result_key = f"video_generation_result_{model.name}"

    st.divider()

    preview_handles: dict[str, DeltaGenerator] = {}

    def render_preview_panel() -> None:
        st.markdown("#### Prediction status / preview")
        preview_handles["status"] = st.empty()
        preview_handles["progress"] = st.empty()
        result_area = st.empty()
        preview_handles["result"] = result_area
        latest_result = st.session_state.get(result_key)
        if latest_result:
            with result_area.container():
                render_video_result(latest_result)
        else:
            preview_handles["status"].info(
                "Run a generation and the live status plus final preview will stay "
                "open here."
            )

    def render_model_selector() -> None:
        st.markdown("#### Model")
        st.selectbox(
            "Choose a model",
            range(len(VIDEO_MODELS)),
            format_func=lambda i: VIDEO_MODELS[i].display_name,
            key="video_model",
            help="Pick the model before writing prompts or adding reference media.",
        )

    kwargs = render_generation_form(
        model,
        preview_renderer=render_preview_panel,
        model_selector_renderer=render_model_selector,
    )

    if kwargs is not None:
        validation_kwargs = dict(kwargs)
        uploaded_for_validation = validation_kwargs.pop("_uploaded_image", None)
        if uploaded_for_validation is not None:
            validation_kwargs["image"] = uploaded_for_validation

        try:
            validate_params(model, validation_kwargs)
        except Exception as exc:
            st.error(f"Invalid parameters:\n\n{exc}")
            return

        status_line = preview_handles.get("status") or st.empty()
        progress_line = preview_handles.get("progress") or st.empty()
        result_area = preview_handles.get("result") or st.empty()
        status_line.info(
            f"Generating with {model.display_name}… the preview will appear here."
        )
        try:
            uploaded = kwargs.pop("_uploaded_image", None)
            if uploaded is not None and model.supports_image:
                uploaded.seek(0)
                kwargs["image"] = uploaded

            start_time = monotonic()

            def progress_callback(event: str, prediction: object) -> None:
                elapsed = format_duration(monotonic() - start_time)
                pred_id = getattr(prediction, "id", "")
                pred_status = getattr(prediction, "status", event)
                progress_line.write(
                    f"Replicate status: `{pred_status}` · elapsed {elapsed}"
                    + (f" · prediction `{pred_id}`" if pred_id else "")
                )

            kwargs["progress_callback"] = progress_callback
            with st.spinner("Waiting for Replicate to finish…"):
                result = get_generation_service().generate(
                    model.name,
                    model.model_type,
                    **kwargs,
                )
            st.session_state[result_key] = result

            if result["success"]:
                status_line.success("Generation complete — preview ready.")
            else:
                status_line.error("Generation failed — details below.")
            with result_area.container():
                render_video_result(result)
        except Exception as exc:
            result = {
                "success": False,
                "error": friendly_error_message(exc),
                "predict_time": 0,
                "estimated_cost": 0,
            }
            st.session_state[result_key] = result
            status_line.error("Generation error — details below.")
            with result_area.container():
                st.error(f"Unexpected error: {friendly_error_message(exc)}")

