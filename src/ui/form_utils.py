"""Shared helpers for Streamlit generation forms."""

from __future__ import annotations

from src.models_config import ModelConfig


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
