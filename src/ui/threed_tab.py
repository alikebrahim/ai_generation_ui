"""3D generation tab for Streamlit app."""

from __future__ import annotations

from time import monotonic

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from src import utils as app_utils
from src.generation_service import get_generation_service
from src.models_config import THREED_MODELS
from src.ui.forms import render_generation_form
from src.ui.result_views import render_3d_result
from src.validation import validate_params

format_duration = app_utils.format_duration
friendly_error_message = app_utils.friendly_error_message


def render_3d_tab() -> None:
    """Render the 3D generation tab."""
    st.header("3D Generation")
    st.caption(
        "Create a mesh or previewable 3D asset, then keep the result visible below."
    )

    threed_idx = int(st.session_state.get("3d_model", 0))
    if threed_idx < 0 or threed_idx >= len(THREED_MODELS):
        threed_idx = 0
    model_3d = THREED_MODELS[threed_idx]
    result_key = f"threed_generation_result_{model_3d.name}"

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
                render_3d_result(latest_result)
        else:
            preview_handles["status"].info(
                "Run a generation and the live status plus final preview will stay "
                "open here."
            )

    def render_model_selector() -> None:
        st.markdown("#### Model")
        st.selectbox(
            "Choose a model",
            range(len(THREED_MODELS)),
            format_func=lambda i: THREED_MODELS[i].display_name,
            key="3d_model",
            help="Pick the model before writing prompts or adding subject images.",
        )

    kwargs_3d = render_generation_form(
        model_3d,
        preview_renderer=render_preview_panel,
        model_selector_renderer=render_model_selector,
    )

    if kwargs_3d is not None:
        validation_kwargs = dict(kwargs_3d)
        uploaded_for_validation = validation_kwargs.pop("_uploaded_image", None)
        if uploaded_for_validation is not None and model_3d.supports_image:
            validation_kwargs["image"] = uploaded_for_validation

        try:
            validate_params(model_3d, validation_kwargs)
        except Exception as exc:
            st.error(f"Invalid parameters:\n\n{exc}")
            return

        status_line = preview_handles.get("status") or st.empty()
        progress_line = preview_handles.get("progress") or st.empty()
        result_area = preview_handles.get("result") or st.empty()
        status_line.info(
            f"Generating with {model_3d.display_name}… the preview will appear here."
        )
        try:
            uploaded = kwargs_3d.pop("_uploaded_image", None)
            if uploaded is not None and model_3d.supports_image:
                uploaded.seek(0)
                kwargs_3d["image"] = uploaded

            start_time = monotonic()

            def progress_callback(event: str, prediction: object) -> None:
                elapsed = format_duration(monotonic() - start_time)
                pred_id = getattr(prediction, "id", "")
                pred_status = getattr(prediction, "status", event)
                progress_line.write(
                    f"Replicate status: `{pred_status}` · elapsed {elapsed}"
                    + (f" · prediction `{pred_id}`" if pred_id else "")
                )

            kwargs_3d["progress_callback"] = progress_callback
            with st.spinner("Waiting for Replicate to finish…"):
                result = get_generation_service().generate(
                    model_3d.name,
                    model_3d.model_type,
                    **kwargs_3d,
                )
            st.session_state[result_key] = result

            if result["success"]:
                status_line.success("Generation complete — preview ready.")
            else:
                status_line.error("Generation failed — details below.")
            with result_area.container():
                render_3d_result(result)
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

