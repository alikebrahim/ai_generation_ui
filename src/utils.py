"""Utility functions — formatting, serialization, and Replicate output helpers."""

from __future__ import annotations

import json
from collections.abc import Mapping, Sequence
from typing import Any


def format_cost(cost: float) -> str:
    """Format a dollar amount for display. e.g. 0.42 → '$0.42'."""
    if cost < 0.01:
        return "< $0.01"
    return f"${cost:.2f}"


def format_duration(seconds: float) -> str:
    """Human-readable duration from seconds."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    if seconds < 3600:
        return f"{seconds / 60:.1f}m"
    return f"{seconds / 3600:.1f}h"


def format_timestamp(ts: str) -> str:
    """Return a shorter display timestamp (YYYY-MM-DD HH:MM)."""
    return ts[:16] if len(ts) >= 16 else ts


def output_to_url(value: Any) -> str:
    """Normalize Replicate output values to a displayable ephemeral URL string.

    Replicate client 1.0+ may return FileOutput objects for generated files.
    Those objects expose a `.url` attribute; older versions and some APIs return
    plain strings, lists, or dicts. This helper keeps UI/database code insulated
    from those representation differences.
    """
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if hasattr(value, "url"):
        return str(value.url)
    if isinstance(value, Mapping):
        for key in (
            "url",
            "uri",
            "model_file",
            "mesh",
            "video",
            "output",
            "file",
        ):
            if key in value:
                url = output_to_url(value[key])
                if url:
                    return url
        return ""
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        for item in value:
            url = output_to_url(item)
            if url:
                return url
        return ""
    return str(value)


def safe_json_value(value: Any) -> Any:
    """Convert arbitrary values into JSON-safe metadata.

    File-like objects and Replicate FileOutput objects must not be serialized
    directly into SQLite history. Keep enough metadata for history/debugging
    without storing bytes or non-serializable handles.
    """
    if value is None or isinstance(value, (str, int, float, bool)):
        return value
    if isinstance(value, Mapping):
        return {str(k): safe_json_value(v) for k, v in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [safe_json_value(v) for v in value]
    if isinstance(value, (bytes, bytearray)):
        return f"<{len(value)} bytes>"
    if hasattr(value, "url"):
        return output_to_url(value)
    if hasattr(value, "name") or hasattr(value, "type"):
        return uploaded_file_metadata(value)
    try:
        json.dumps(value)
        return value
    except TypeError:
        return str(value)


def sanitize_parameters(parameters: dict | None) -> dict:
    """Return JSON-serializable generation parameters for SQLite history."""
    return safe_json_value(parameters or {})


def uploaded_file_metadata(uploaded: Any) -> dict[str, Any]:
    """Small, safe metadata record for a Streamlit UploadedFile-like object."""
    if uploaded is None:
        return {}
    size = getattr(uploaded, "size", None)
    if size is None and hasattr(uploaded, "getbuffer"):
        try:
            size = len(uploaded.getbuffer())
        except Exception:
            size = None
    return {
        "filename": getattr(uploaded, "name", "uploaded-file"),
        "mime_type": getattr(uploaded, "type", None),
        "size_bytes": size,
    }


def estimate_cost_label(model_id: str, duration: float | None, calculator) -> str:
    """Best-effort pre-generation cost label for the current form."""
    if duration:
        return format_cost(calculator(model_id, 0, output_duration=duration))
    return "Cost shown after generation"
