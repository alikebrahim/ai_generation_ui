"""Image tab workflow filters and model-picker copy."""

from __future__ import annotations

import streamlit as st

from src.image_models_config import IMAGE_MODELS
from src.models_config import ModelConfig

IMAGE_WORKFLOW_FILTERS: list[tuple[str, str]] = [
    ("all", "All images"),
    ("text_to_image", "Text to image"),
    ("image_edit", "Edit with references"),
    ("fast_draft", "Fast & cheap"),
    ("max_quality", "Max quality"),
    ("typography", "Text in image"),
    ("vector_svg", "Vector / SVG"),
    ("design", "Design-first"),
]


def filter_models_for_workflow(
    models: list[ModelConfig], workflow_key: str
) -> list[ModelConfig]:
    """Return models matching the selected image workflow filter."""
    if workflow_key == "all":
        return list(models)
    return [
        m
        for m in models
        if workflow_key in getattr(m, "workflow_tags", [])
    ]


def render_workflow_filter() -> str:
    """Render segmented workflow filter; return selected key."""
    labels = {key: label for key, label in IMAGE_WORKFLOW_FILTERS}
    options = [key for key, _ in IMAGE_WORKFLOW_FILTERS]
    default = st.session_state.get("image_workflow_filter", "all")
    if default not in options:
        default = "all"
    selected = st.segmented_control(
        "What do you want to create?",
        options=options,
        default=default,
        format_func=lambda key: labels[key],
        key="image_workflow_filter",
        help="Narrows models by provider-stated strengths and workflow type.",
    )
    return selected or default


def resolve_image_model_selection(
    filtered_models: list[ModelConfig],
) -> ModelConfig:
    """Model selectbox backed by session state."""
    if not filtered_models:
        return IMAGE_MODELS[0]
    names = [m.name for m in filtered_models]
    default_name = st.session_state.get("image_model_name", names[0])
    if default_name not in names:
        default_name = names[0]
    idx = names.index(default_name)
    picked = st.selectbox(
        "Image model",
        options=names,
        index=idx,
        format_func=lambda n: next(
            m.display_name for m in filtered_models if m.name == n
        ),
        key="image_model_select",
        label_visibility="collapsed",
    )
    st.session_state["image_model_name"] = picked
    return next(m for m in filtered_models if m.name == picked)
