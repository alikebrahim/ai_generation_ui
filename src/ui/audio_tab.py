"""Audio generation tab — music and speech."""

from __future__ import annotations

import streamlit as st

from src.audio_models_config import AUDIO_MODELS, MUSIC_MODELS
from src.models_config import ModelConfig
from src.ui.audio_forms import render_audio_generation_form
from src.ui.generation_panel import build_preview_panel, run_model_generation
from src.ui.result_views import render_audio_result
from src.validation import validate_params

AUDIO_WORKFLOW_FILTERS: list[tuple[str, str]] = [
    ("all", "All audio"),
    ("music", "Make music"),
    ("speech", "Generate speech"),
]


def filter_audio_models(
    models: list[ModelConfig], workflow_key: str
) -> list[ModelConfig]:
    if workflow_key == "all":
        return list(models)
    return [m for m in models if workflow_key in getattr(m, "workflow_tags", [])]


def render_audio_workflow_filter() -> str:
    labels = {key: label for key, label in AUDIO_WORKFLOW_FILTERS}
    options = [key for key, _ in AUDIO_WORKFLOW_FILTERS]
    default = st.session_state.get("audio_workflow_filter", "all")
    if default not in options:
        default = "all"
    return st.radio(
        "What do you want to create?",
        options=options,
        index=options.index(default),
        format_func=lambda key: labels[key],
        horizontal=True,
        key="audio_workflow_filter",
        help="Narrows models to music or speech workflows.",
    )


def _consume_pending_remix(expected_type: str) -> None:
    remix = st.session_state.pop("pending_remix", None)
    if not remix:
        return
    if str(remix.get("model_type", "")).lower() != expected_type:
        st.session_state["pending_remix"] = remix
        return
    mname = str(remix.get("model_name") or "")
    if mname:
        st.session_state["audio_model_name"] = mname
        st.session_state["audio_workflow_filter"] = "all"
    params = remix.get("params") or {}
    prompt = remix.get("prompt") or ""
    if mname:
        for field in ("lyrics", "text", "prompt"):
            if prompt and field in ("lyrics", "text", "prompt"):
                st.session_state[f"audio_{mname}_{field}"] = prompt
                break
        for pname, pval in params.items() if isinstance(params, dict) else []:
            for field in ("lyrics", "text", "prompt"):
                if pname == field:
                    st.session_state[f"audio_{mname}_{field}"] = pval
            for is_adv in (False, True):
                k = f"{mname}_{'adv_' if is_adv else ''}{pname}"
                try:
                    st.session_state[k] = pval
                except Exception:
                    pass
    if prompt or params:
        st.toast("Loaded from History.")


def render_audio_tab() -> None:
    """Render the Audio tab."""
    st.header("Audio Generation")
    st.caption(
        "Create music or spoken audio with Replicate. Pick a workflow, choose a "
        "model, then generate in the preview panel."
    )

    _consume_pending_remix("audio")

    workflow_key = render_audio_workflow_filter()
    filtered = filter_audio_models(AUDIO_MODELS, workflow_key)
    if not filtered:
        st.warning("No models match this filter. Showing all audio models.")
        filtered = list(AUDIO_MODELS)

    names = [m.name for m in filtered]
    current = st.session_state.get("audio_model_name")
    if current not in names:
        current = names[0]
        st.session_state["audio_model_name"] = current
    model = next((m for m in filtered if m.name == current), filtered[0])

    st.divider()
    with st.container(border=True):
        st.markdown("#### Model")
        idx = names.index(model.name)
        chosen = st.selectbox(
            "Choose a model",
            options=names,
            index=idx,
            format_func=lambda n: next(
                (m.display_name for m in AUDIO_MODELS if m.name == n), n
            ),
            key="audio_model_name",
        )
        model = next((m for m in filtered if m.name == chosen), model)
        category = (
            "Music" if model in MUSIC_MODELS else "Speech"
        )
        st.caption(f"{category} · {model.output_notes or model.pricing_notes or ''}")

    result_key = f"audio_generation_result_{model.name}"
    preview_handles, render_preview_panel = build_preview_panel(
        result_key=result_key,
        model_type="audio",
        render_result=render_audio_result,
    )

    kwargs = render_audio_generation_form(
        model,
        preview_renderer=render_preview_panel,
    )

    if kwargs is not None:
        try:
            validate_params(model, kwargs)
        except Exception as exc:
            st.error(f"Invalid parameters:\n\n{exc}")
            return

        run_model_generation(
            model=model,
            handles=preview_handles,
            result_key=result_key,
            kwargs=kwargs,
            render_result=render_audio_result,
        )
