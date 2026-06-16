"""Shared model-picker caption from provider metadata."""

from __future__ import annotations

from src.models_config import ModelConfig


def model_caption(model: ModelConfig) -> str:
    """Plain-English model picker caption from provider metadata."""
    parts: list[str] = []
    if model.provider_category:
        parts.append(f"**{model.provider_category}**")
    if model.provider_summary:
        parts.append(model.provider_summary)
    if model.strength_tags:
        tags = ", ".join(tag.replace("_", " ") for tag in model.strength_tags[:5])
        parts.append(f"Good at: {tags}.")
    if parts:
        return " ".join(parts)
    if model.output_notes:
        return model.output_notes
    if model.pricing_notes:
        return model.pricing_notes
    return ""
