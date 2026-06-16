"""Shared helpers for Streamlit generation forms."""

from __future__ import annotations

from typing import Any

from src.models_config import ModelConfig


def has_upload_value(value: Any) -> bool:
    """Return True when a file uploader holds one or more files."""
    if value is None:
        return False
    if isinstance(value, list):
        return len(value) > 0
    return True


def set_upload_kwarg(kwargs: dict, param: str, uploaded: Any) -> None:
    """Set ``_uploaded_{param}`` only when the user provided a file.

    Empty advanced uploaders must not overwrite values set in the preview column.
    """
    if not has_upload_value(uploaded):
        return
    kwargs[f"_uploaded_{param}"] = uploaded


def preview_owned_file_params(model: ModelConfig) -> frozenset[str]:
    """File params rendered in the multimodal preview column (single site each)."""
    if model.workflow_archetype != "multimodal_video":
        return frozenset()
    owned: set[str] = set()
    if "start_image" in model.file_input_params:
        owned.add("start_image")
    elif "image" in model.file_input_params:
        owned.add("image")
    if "end_image" in model.file_input_params:
        owned.add("end_image")
    if "last_frame_image" in model.file_input_params:
        owned.add("last_frame_image")
    for param in (
        "reference_images",
        "reference_video",
        "reference_videos",
        "reference_audios",
    ):
        if param in model.file_input_params:
            owned.add(param)
    return frozenset(owned)


def normalize_file_kwargs(model: ModelConfig, kwargs: dict) -> dict:
    """Map ``_uploaded_*`` form keys to Replicate payload parameter names.

    Streamlit file uploaders are stored under internal ``_uploaded_*`` keys so
    form rendering can distinguish raw widget state from API parameters. This
    helper converts those internal keys into the names expected by payload
    builders and validation.
    """
    out = dict(kwargs)
    uploaded = out.pop("_uploaded_image", None)
    if uploaded is not None and model.supports_image and "image" not in out:
        out["image"] = uploaded
    for key in list(out.keys()):
        if not key.startswith("_uploaded_"):
            continue
        param = key.removeprefix("_uploaded_")
        value = out.pop(key)
        if param == "images":
            out["_uploaded_images"] = value  # may be list for multi-ref
        else:
            out[param] = value
    return out
