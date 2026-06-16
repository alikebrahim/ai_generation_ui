"""3D generation tab for Streamlit app."""

from __future__ import annotations

import streamlit as st

from src.models_config import THREED_MODELS
from src.ui.form_utils import normalize_file_kwargs
from src.ui.forms import render_generation_form
from src.ui.generation_panel import build_preview_panel, run_model_generation
from src.ui.model_caption import model_caption
from src.ui.result_views import render_3d_result
from src.validation import validate_params


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
    selected = st.segmented_control(
        "What kind of 3D?",
        options=options,
        default=default,
        format_func=lambda key: labels[key],
        key="threed_workflow_filter",
        help="Narrows the 3D models to matching capabilities.",
    )
    return selected or default


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

    st.divider()

    with st.container(border=True):
        st.markdown("#### Model")
        names = [m.name for m in filtered_models]
        current = st.session_state.get("3d_model_name")
        if current not in names:
            current = names[0]
            st.session_state["3d_model_name"] = current
        idx = names.index(current)
        chosen = st.selectbox(
            "Choose a model",
            options=names,
            index=idx,
            format_func=lambda n: next(
                (m.display_name for m in THREED_MODELS if m.name == n), n
            ),
            key="3d_model_name",
            help="Pick the model before writing prompts or adding subject images.",
        )
        if chosen != current:
            st.session_state["3d_model_name"] = chosen
            current = chosen
        model_3d = next(
            (m for m in filtered_models if m.name == current), filtered_models[0]
        )
        caption = model_caption(model_3d)
        if caption:
            st.caption(caption)

    result_key = f"threed_generation_result_{model_3d.name}"

    preview_handles, render_preview_panel = build_preview_panel(
        result_key=result_key,
        model_type="3d",
        render_result=render_3d_result,
    )

    # Unified call (model card is now always rendered in the tab before the form,
    # matching video + audio patterns; renderer callback removed).
    kwargs_3d = render_generation_form(
        model_3d,
        preview_renderer=render_preview_panel,
    )

    if kwargs_3d is not None:
        validation_kwargs = normalize_file_kwargs(model_3d, kwargs_3d)
        try:
            validate_params(model_3d, validation_kwargs)
        except Exception as exc:
            st.error(f"Invalid parameters:\n\n{exc}")
            return

        run_model_generation(
            model=model_3d,
            handles=preview_handles,
            result_key=result_key,
            kwargs=kwargs_3d,
            render_result=render_3d_result,
            use_spinner=True,
            spinner_message="Waiting for Replicate — see status above for updates.",
        )
