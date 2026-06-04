"""3D generation tab for Streamlit app."""

from __future__ import annotations

from time import monotonic

import streamlit as st
from streamlit.delta_generator import DeltaGenerator

from src import utils as app_utils
from src.generation_service import get_generation_service
from src.models_config import THREED_MODELS
from src.ui.form_utils import normalize_file_kwargs
from src.ui.forms import render_generation_form
from src.ui.result_views import render_3d_result
from src.validation import validate_params

format_duration = app_utils.format_duration
friendly_error_message = app_utils.friendly_error_message


def _consume_pending_remix(expected_type: str) -> None:
    """Apply pending History remix data to session state for widget prefill (3D)."""
    remix = st.session_state.pop("pending_remix", None)
    if not remix:
        return
    if str(remix.get("model_type", "")).lower() != expected_type:
        st.session_state["pending_remix"] = remix
        return
    mname = str(remix.get("model_name") or "")
    if mname:
        st.session_state["3d_model_name"] = mname
        st.session_state["threed_workflow_filter"] = "all"  # ensure visible
    prompt = remix.get("prompt") or ""
    params = remix.get("params") or {}
    if mname and prompt:
        st.session_state[f"prompt_{mname}"] = prompt
    for pname, pval in params.items() if isinstance(params, dict) else []:
        if mname:
            for is_adv in (False, True):
                k = f"{mname}_{'adv_' if is_adv else ''}{pname}"
                try:
                    st.session_state[k] = pval
                except Exception:
                    pass
    if prompt or params:
        st.toast("Loaded from History. Re-upload media if needed.")


THREED_WORKFLOW_FILTERS: list[tuple[str, str]] = [
    ("all", "All 3D"),
    ("image_to_3d", "From image"),
    ("text_to_3d", "From text"),
    ("multiview_to_3d", "Multiview"),
    ("texturing", "Mesh texturing"),
]


def filter_3d_models_for_workflow(models, workflow_key: str):
    if workflow_key == "all":
        return list(models)
    return [m for m in models if workflow_key in getattr(m, "workflow_tags", [])]


def render_3d_workflow_filter() -> str:
    labels = {key: label for key, label in THREED_WORKFLOW_FILTERS}
    options = [key for key, _ in THREED_WORKFLOW_FILTERS]
    default = st.session_state.get("threed_workflow_filter", "all")
    if default not in options:
        default = "all"
    selected = st.radio(
        "What kind of 3D?",
        options=options,
        index=options.index(default),
        format_func=lambda key: labels[key],
        horizontal=True,
        key="threed_workflow_filter",
        help="Narrows the 3D models to matching capabilities.",
    )
    return selected


def render_3d_tab() -> None:
    """Render the 3D generation tab."""
    st.header("3D Generation")
    st.caption(
        "Create a mesh or previewable 3D asset, then keep the result visible below."
    )

    _consume_pending_remix("3d")

    workflow_key = render_3d_workflow_filter()
    filtered_models = filter_3d_models_for_workflow(THREED_MODELS, workflow_key)
    if not filtered_models:
        st.warning("No models match this filter. Showing all.")
        filtered_models = list(THREED_MODELS)

    # name-based selection for consistency with Video tab
    names = [m.name for m in filtered_models]
    current = st.session_state.get("3d_model_name")
    if current not in names:
        current = names[0]
        st.session_state["3d_model_name"] = current
    model_3d = next(
        (m for m in filtered_models if m.name == current), filtered_models[0]
    )
    result_key = f"threed_generation_result_{model_3d.name}"

    # show model info similar to Video tab
    model_caption = model_3d.output_notes or model_3d.pricing_notes or ""
    if model_caption:
        st.caption(model_caption)

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
                "open here. 3D generations typically take 1–10 minutes."
            )

    def render_model_selector() -> None:
        st.markdown("#### Model")
        # name-based select; the tab re-resolves model_3d from session key on each run
        current_names = [
            m.name
            for m in (
                filtered_models if "filtered_models" in locals() else THREED_MODELS
            )
        ]
        cur = st.session_state.get("3d_model_name") or current_names[0]
        if cur not in current_names:
            cur = current_names[0]
        idx = current_names.index(cur)
        chosen = st.selectbox(
            "Choose a model",
            options=current_names,
            index=idx,
            format_func=lambda n: next(
                (m.display_name for m in THREED_MODELS if m.name == n), n
            ),
            key="3d_model_name",
            help="Pick the model before writing prompts or adding subject images.",
        )
        if chosen != cur:
            st.session_state["3d_model_name"] = chosen

    kwargs_3d = render_generation_form(
        model_3d,
        preview_renderer=render_preview_panel,
        model_selector_renderer=render_model_selector,
    )

    if kwargs_3d is not None:
        validation_kwargs = normalize_file_kwargs(model_3d, kwargs_3d)
        try:
            validate_params(model_3d, validation_kwargs)
        except Exception as exc:
            st.error(f"Invalid parameters:\n\n{exc}")
            return

        status_line = preview_handles.get("status") or st.empty()
        progress_line = preview_handles.get("progress") or st.empty()
        result_area = preview_handles.get("result") or st.empty()
        status_line.info(
            f"Generating with {model_3d.display_name}… preview here. "
            "Typically 1–10 min (longer for complex). Status below."
        )
        try:
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
            with st.spinner(
                "Waiting for Replicate… (3D often 1-10+ min; see status above)"
            ):
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
