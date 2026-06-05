"""Utility functions — formatting, serialization, and Replicate output helpers."""

from __future__ import annotations

import base64
import json
import time
from collections.abc import Mapping, Sequence
from pathlib import Path
from typing import Any
from urllib.parse import urlparse

import requests


def format_cost(cost: float) -> str:
    """Format a dollar amount for display. e.g. 0.42 → '$0.42'."""
    if cost < 0:
        return "Cost unknown"
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


_IMAGE_SIGNATURES = (
    (b"\xff\xd8\xff", ".jpg", "image/jpeg"),
    (b"\x89PNG\r\n\x1a\n", ".png", "image/png"),
)

_IMAGE_MIME_BY_EXTENSION = {
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}

_EXTENSION_BY_MIME = {
    "image/jpeg": ".jpg",
    "image/jpg": ".jpg",
    "image/png": ".png",
    "image/webp": ".webp",
}


def _read_file_like_bytes(file_obj: Any) -> bytes:
    """Read bytes from a file-like object without depending on its class."""
    if isinstance(file_obj, bytes):
        return file_obj
    if isinstance(file_obj, bytearray):
        return bytes(file_obj)
    if hasattr(file_obj, "getvalue"):
        value = file_obj.getvalue()
        return value.encode("utf-8") if isinstance(value, str) else bytes(value)
    if hasattr(file_obj, "getbuffer"):
        return bytes(file_obj.getbuffer())
    if hasattr(file_obj, "read"):
        try:
            pos = file_obj.tell()
        except Exception:
            pos = None
        try:
            file_obj.seek(0)
        except Exception:
            pass
        value = file_obj.read()
        if pos is not None:
            try:
                file_obj.seek(pos)
            except Exception:
                pass
        return value.encode("utf-8") if isinstance(value, str) else bytes(value)
    raise ValueError("Unsupported image input; expected bytes or a file-like object.")


def _sniff_image_type(data: bytes) -> tuple[str, str] | None:
    """Return (extension, MIME type) for supported image bytes."""
    for signature, extension, mime_type in _IMAGE_SIGNATURES:
        if data.startswith(signature):
            return extension, mime_type
    if len(data) >= 12 and data[:4] == b"RIFF" and data[8:12] == b"WEBP":
        return ".webp", "image/webp"
    return None


def image_to_data_uri(
    image: Any,
    *,
    allowed_extensions: set[str] | None = None,
    max_size_bytes: int | None = None,
) -> str:
    """Convert an uploaded/local image into a MIME-specific data URI.

    Replicate's file-upload URLs do not always preserve a filename extension in
    the URL. Some model backends, including Hunyuan 3D 3.1, validate the image
    URL suffix and reject extensionless file URLs. A data URI keeps the image
    format explicit without creating a paid prediction during conversion.
    """
    if isinstance(image, str):
        return image

    filename = str(getattr(image, "name", "") or "")
    declared_mime = str(getattr(image, "type", "") or "").lower()
    data = _read_file_like_bytes(image)

    if max_size_bytes is not None and len(data) > max_size_bytes:
        size_mb = len(data) / 1_000_000
        limit_mb = max_size_bytes / 1_000_000
        raise ValueError(
            f"Image is too large for this model: {size_mb:.2f} MB. "
            f"Maximum is {limit_mb:.2f} MB.",
        )

    extension = Path(filename).suffix.lower()
    mime_type = _IMAGE_MIME_BY_EXTENSION.get(extension)

    sniffed = _sniff_image_type(data)
    if sniffed is not None:
        sniffed_extension, sniffed_mime = sniffed
        if not extension:
            extension = sniffed_extension
        if mime_type is None:
            mime_type = sniffed_mime

    if mime_type is None and declared_mime:
        extension = extension or _EXTENSION_BY_MIME.get(declared_mime, "")
        mime_type = _IMAGE_MIME_BY_EXTENSION.get(extension) or declared_mime

    allowed = allowed_extensions or set(_IMAGE_MIME_BY_EXTENSION)
    if extension not in allowed or mime_type not in _IMAGE_MIME_BY_EXTENSION.values():
        supported = ", ".join(sorted(allowed))
        raise ValueError(
            f"Unsupported image format: {extension}. "
            f"Supported formats: {supported}.",
        )

    encoded = base64.b64encode(data).decode("ascii")
    return f"data:{mime_type};base64,{encoded}"


def estimate_cost_label(model_id: str, duration: float | None, calculator) -> str:
    """Best-effort pre-generation cost label for the current form."""
    if duration is not None and duration > 0:
        return format_cost(calculator(model_id, 0, output_duration=duration))
    return "Cost shown after generation"


def _replicate_error_text(error: Any) -> tuple[str, int | None]:
    """Extract message and HTTP status from a ReplicateError when present."""
    detail = getattr(error, "detail", None)
    status = getattr(error, "status", None)
    if detail is not None and str(detail).strip():
        text = str(detail)
    else:
        text = str(error)
    try:
        status_code = int(status) if status is not None else None
    except (TypeError, ValueError):
        status_code = None
    if status_code is None and "status:" in text.lower():
        for token in text.replace(":", " ").split():
            if token.isdigit() and len(token) == 3:
                status_code = int(token)
                break
    return text, status_code


def technical_error_detail(error: Exception | str | None) -> str | None:
    """Return raw technical detail when it differs from the friendly message."""
    if error is None:
        return None
    raw = str(error).strip()
    if not raw:
        return None
    friendly = friendly_error_message(error)
    if raw == friendly:
        return None
    return raw


def friendly_error_message(error: Exception | str) -> str:
    """Translate common Replicate/API failures into actionable UI copy."""
    text, status_code = (
        _replicate_error_text(error)
        if not isinstance(error, str)
        else (error, None)
    )
    if isinstance(error, str):
        text = error
        lower = text.lower()
        for token in text.replace(":", " ").split():
            if token.isdigit() and len(token) == 3:
                status_code = int(token)
                break
    else:
        lower = text.lower()

    if status_code == 401 or "status: 401" in lower or "unauthorized" in lower:
        return (
            "Replicate could not authenticate this request. Check that your "
            "REPLICATE_API_TOKEN in .env is present and valid."
        )
    if (
        status_code == 402
        or "insufficient credit" in lower
        or "payment required" in lower
    ):
        return (
            "Replicate reported insufficient account credit. Add billing credit "
            "on replicate.com, then try again."
        )
    if status_code == 403 or "forbidden" in lower:
        return (
            "Replicate denied access to this model or resource. Confirm your "
            "account can run this model and that the model ID is correct."
        )
    if status_code == 404 or "status: 404" in lower or "not found" in lower:
        return (
            "Replicate could not find the requested model endpoint or model "
            "version. This can happen when a model requires a versioned API call "
            "or when the model ID changed."
        )
    if status_code == 422 or "status: 422" in lower or "validation" in lower:
        return (
            "Replicate rejected one of the settings for this model. Review the "
            "visible controls and try the recommended/default values."
        )
    if status_code == 429 or "rate limit" in lower or "too many requests" in lower:
        return (
            "Replicate is rate-limiting requests. Wait a minute and try again."
        )
    if status_code in (500, 502, 503) or "internal server" in lower:
        return (
            "Replicate had a temporary server problem. Wait a few minutes and "
            "try again; if it persists, check replicate.com/status."
        )
    if "canceled" in lower or "cancelled" in lower:
        return "This job was canceled before it finished."
    if any(
        phrase in lower
        for phrase in (
            "content policy",
            "safety",
            "nsfw",
            "moderation",
            "blocked",
            "not allowed",
        )
    ):
        return (
            "Replicate declined this request for content or safety reasons. "
            "Try a different prompt or image."
        )
    if "timeout" in lower or "timed out" in lower:
        return (
            "The request timed out before Replicate finished. Try again; "
            "longer jobs may need a simpler prompt or smaller settings."
        )
    if "connection" in lower or "network" in lower or "connectionerror" in lower:
        return (
            "The request could not reach Replicate reliably. Check the network "
            "connection or try again in a few minutes."
        )
    if "replicate_api_token" in lower or "api token" in lower and "missing" in lower:
        return (
            "No Replicate API token is configured. Add REPLICATE_API_TOKEN to "
            "your .env file."
        )
    if "status: failed" in lower or lower.strip() == "failed":
        return (
            "Replicate reported that the job failed. Open the prediction link "
            "below for more detail, or adjust your inputs and try again."
        )
    if len(text) > 280 and ("traceback" in lower or "replicateerror" in lower):
        return (
            "Something went wrong talking to Replicate. Check your token, "
            "network, and inputs — technical details are in the expander below."
        )
    return text


def download_output(
    url: str,
    dest_dir: Path,
    prefix: str = "output",
    timeout: int = 120,
) -> dict:
    """Download a provider output URL to a local file.

    Tries to determine the extension from the URL path or Content-Type
    header, falling back to ``.bin``.

    Args:
        url: Ephemeral URL to download.
        dest_dir: Directory to save into (created if absent).
        prefix: Basename prefix before the timestamp (e.g. ``video``,
                ``model``, ``preview``).
        timeout: Download timeout in seconds.

    Returns:
        A dict with ``success`` (bool), ``local_path`` (str | None),
        ``file_size_bytes`` (int | None), and ``error`` (str | None).
    """
    if not url:
        return {
            "success": False,
            "local_path": None,
            "file_size_bytes": None,
            "error": "No URL provided to download.",
        }

    dest_dir.mkdir(parents=True, exist_ok=True)
    try:
        resp = requests.get(url, stream=True, timeout=timeout)
        resp.raise_for_status()

        # Determine extension from URL path or Content-Type
        content_type = resp.headers.get("content-type", "")
        if url.endswith(".mp4") or "video/mp4" in content_type:
            ext = ".mp4"
        elif url.endswith(".glb") or "model/gltf" in content_type:
            ext = ".glb"
        elif url.endswith(".obj") or "model/obj" in content_type:
            ext = ".obj"
        elif url.endswith(".png") or "image/png" in content_type:
            ext = ".png"
        elif (
            url.endswith(".jpg")
            or url.endswith(
                ".jpeg",
            )
            or "image/jpeg" in content_type
        ):
            ext = ".jpg"
        elif url.endswith(".mp3") or "audio/mpeg" in content_type:
            ext = ".mp3"
        elif url.endswith(".wav") or "audio/wav" in content_type:
            ext = ".wav"
        elif url.endswith(".m4a") or "audio/mp4" in content_type:
            ext = ".m4a"
        elif url.endswith(".flac") or "audio/flac" in content_type:
            ext = ".flac"
        else:
            # Guess from the URL path without query-string tokens.
            url_path = urlparse(url).path.rstrip("/").rsplit("/", 1)[-1]
            ext = Path(url_path).suffix if url_path and "." in url_path else ".bin"

        timestamp = time.strftime("%Y%m%d-%H%M%S")
        unique_suffix = time.time_ns() % 1_000_000_000
        filename = f"{prefix}-{timestamp}-{unique_suffix:09d}{ext}"
        local_path = dest_dir / filename

        with open(local_path, "wb") as f:
            for chunk in resp.iter_content(chunk_size=8192):
                f.write(chunk)

        file_size = local_path.stat().st_size
        return {
            "success": True,
            "local_path": str(local_path),
            "file_size_bytes": file_size,
            "error": None,
        }
    except requests.RequestException as e:
        return {
            "success": False,
            "local_path": None,
            "file_size_bytes": None,
            "error": str(e),
        }
