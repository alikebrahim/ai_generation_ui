"""Plain-English summary of attached media before generation."""

from __future__ import annotations

import streamlit as st

from src.models_config import ModelConfig
from src.ui.form_utils import has_upload_value, preview_owned_file_params


def _label_for_param(model: ModelConfig, param: str) -> str:
    return model.media_roles.get(param, param.replace("_", " ").title())


def collect_attached_media_labels(model: ModelConfig, kwargs: dict) -> list[str]:
    """Return human labels for uploads present in form kwargs."""
    labels: list[str] = []
    seen: set[str] = set()

    if has_upload_value(kwargs.get("_uploaded_image")):
        labels.append(_label_for_param(model, "image"))
        seen.add("image")

    for param in sorted(model.file_input_params):
        if param in seen:
            continue
        if has_upload_value(kwargs.get(f"_uploaded_{param}")):
            labels.append(_label_for_param(model, param))
            seen.add(param)

    if model.name == "rodin" and has_upload_value(kwargs.get("_uploaded_images")):
        labels.append(_label_for_param(model, "images"))

    for param in ("image", "video"):
        if param in model.required_file_params and param not in seen:
            if has_upload_value(kwargs.get(f"_uploaded_{param}")):
                labels.append(_label_for_param(model, param))

    return labels


def infer_workflow_hint(model: ModelConfig, kwargs: dict) -> str:
    """Short hint for text-only vs image-guided generation."""
    if model.workflow_archetype == "motion_transfer":
        return "Motion transfer (character image + driving video)"
    if model.workflow_archetype == "video_edit":
        return "Video edit (source video + instructions)"
    if model.workflow_archetype != "multimodal_video":
        if has_upload_value(kwargs.get("_uploaded_image")):
            return "Image-to-video (start image attached)"
        return "Text-to-video (no start image)"

    preview_params = preview_owned_file_params(model)
    start_keys = {"start_image", "image"} & preview_params
    has_start = any(
        has_upload_value(kwargs.get(f"_uploaded_{p}")) for p in start_keys
    )
    end_keys = {"end_image", "last_frame_image"} & preview_params
    has_end = any(has_upload_value(kwargs.get(f"_uploaded_{p}")) for p in end_keys)
    has_refs = any(
        has_upload_value(kwargs.get(f"_uploaded_{p}"))
        for p in preview_params
        if p.startswith("reference")
    )

    if has_refs:
        return "Multimodal (reference media attached)"
    if has_start and has_end:
        return "Image-to-video with start and end frames"
    if has_start:
        return "Image-to-video (start frame attached)"
    return "Text-to-video (no frames attached)"


def render_media_attachment_summary(model: ModelConfig, kwargs: dict) -> None:
    """Show what media will be sent before the user clicks Generate."""
    labels = collect_attached_media_labels(model, kwargs)
    hint = infer_workflow_hint(model, kwargs)
    if labels:
        st.caption(f"**Attached media:** {' · '.join(labels)}")
    else:
        st.caption("**Attached media:** none")
    st.caption(f"**Likely mode:** {hint}")
