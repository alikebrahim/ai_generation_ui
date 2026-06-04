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
from src.ui.video_workflow import (
    filter_models_for_workflow,
    model_caption,
    render_workflow_filter,
    resolve_video_model_selection,
)
from src.validation import validate_params

format_duration = app_utils.format_duration
friendly_error_message = app_utils.friendly_error_message


def render_video_tab() -> None:
    """Render the video generation tab."""
    st.header("Video Generation")
    st.caption(
        "Pick what you want to do, choose a matching model, then generate in the "
        "preview panel."
    )

    workflow_key = render_workflow_filter()
    filtered_models = filter_models_for_workflow(VIDEO_MODELS, workflow_key)
    if not filtered_models:
        st.warning("No models match this workflow filter. Try “All models”.")
        filtered_models = list(VIDEO_MODELS)

    st.divider()

    with st.container(border=True):
        st.markdown("#### Model")
        model = resolve_video_model_selection(filtered_models)
        caption = model_caption(model)
        if caption:
            st.caption(caption)

    result_key = f"video_generation_result_{model.name}"

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

    kwargs = render_generation_form(
        model,
        preview_renderer=render_preview_panel,
    )

    if kwargs is not None:
        validation_kwargs = dict(kwargs)
        for upload_key, param in (
            ("_uploaded_image", "image"),
            ("_uploaded_video", "video"),
            ("_uploaded_start_image", "start_image"),
        ):
            uploaded = validation_kwargs.pop(upload_key, None)
            if uploaded is not None:
                validation_kwargs[param] = uploaded
        for key in list(validation_kwargs.keys()):
            if key.startswith("_uploaded_"):
                param = key.removeprefix("_uploaded_")
                if validation_kwargs[key] is not None:
                    validation_kwargs[param] = validation_kwargs[key]

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
            start_time = monotonic()

            def progress_callback(event: str, prediction: object) -> None:
                elapsed = format_duration(monotonic() - start_time)
                pred_id = getattr(prediction, "id", "")
                pred_status = getattr(prediction, "status", event)
                progress_line.write(
                    f"Status: **{pred_status}** · {elapsed} elapsed · id `{pred_id}`"
                )

            result = get_generation_service().generate(
                model.name,
                "video",
                progress_callback=progress_callback,
                **kwargs,
            )
            st.session_state[result_key] = result
            progress_line.empty()
            if result.get("success"):
                status_line.success("Generation complete.")
                with result_area.container():
                    render_video_result(result)
            else:
                status_line.error(
                    friendly_error_message(result.get("error", "Generation failed"))
                )
        except Exception as exc:
            progress_line.empty()
            status_line.error(friendly_error_message(exc))
