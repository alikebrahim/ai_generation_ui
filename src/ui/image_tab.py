"""Image generation tab."""

from __future__ import annotations

import streamlit as st

from src.image_models_config import IMAGE_MODELS
from src.replicate_payload import prepare_payload_for_model
from src.ui.forms import render_generation_form
from src.ui.generation_panel import build_preview_panel, run_model_generation
from src.ui.image_workflow import (
    filter_models_for_workflow,
    render_workflow_filter,
    resolve_image_model_selection,
)
from src.ui.model_caption import model_caption
from src.ui.result_views import render_image_result
from src.validation import ValidationError


def _consume_pending_remix(expected_type: str) -> None:
    """Apply pending History remix data to session state for widget prefill."""
    remix = st.session_state.pop("pending_remix", None)
    if not remix:
        return
    if str(remix.get("model_type", "")).lower() != expected_type:
        st.session_state["pending_remix"] = remix
        return
    mname = str(remix.get("model_name") or "")
    if mname:
        st.session_state["image_model_name"] = mname
        st.session_state["image_workflow_filter"] = "all"
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
        st.toast("Loaded from History. Re-upload reference images if needed.")


def render_image_tab() -> None:
    """Render the image generation tab."""
    st.header("Image Generation")
    st.caption(
        "Pick a workflow, choose a model, then generate. Each model shows a "
        "short provider summary so you can match the tool to the task."
    )

    _consume_pending_remix("image")

    workflow_key = render_workflow_filter()
    filtered_models = filter_models_for_workflow(IMAGE_MODELS, workflow_key)
    if not filtered_models:
        st.warning("No models match this workflow filter. Try “All images”.")
        filtered_models = list(IMAGE_MODELS)

    st.divider()

    with st.container(border=True):
        st.markdown("#### Model")
        model = resolve_image_model_selection(filtered_models)
        caption = model_caption(model)
        if caption:
            st.caption(caption)

    result_key = f"image_generation_result_{model.name}"
    preview_handles, render_preview_panel = build_preview_panel(
        result_key=result_key,
        model_type="image",
        render_result=render_image_result,
    )

    kwargs = render_generation_form(model, preview_renderer=render_preview_panel)
    if kwargs is None:
        return

    try:
        prepare_payload_for_model(model, **kwargs)
    except ValidationError as exc:
        st.error(str(exc))
        return

    run_model_generation(
        model=model,
        handles=preview_handles,
        result_key=result_key,
        kwargs=kwargs,
        render_result=render_image_result,
    )
