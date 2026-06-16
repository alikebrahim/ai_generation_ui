"""Shared generation progress labels, thresholds, and status copy."""

from __future__ import annotations

from time import monotonic
from typing import Any

from src.utils import format_duration

# Seconds before showing "taking longer than usual" (model-type defaults).
LONG_WAIT_THRESHOLDS: dict[str, float] = {
    "video": 180.0,
    "3d": 420.0,
    "audio": 90.0,
    "image": 120.0,
}

REPLICATE_STATUS_LABELS: dict[str, str] = {
    "starting": "Waiting in queue",
    "processing": "Running on Replicate",
    "succeeded": "Complete",
    "failed": "Failed",
    "canceled": "Canceled",
    "cancelled": "Canceled",
}


def long_wait_threshold_seconds(model_type: str) -> float:
    """Return elapsed seconds before a long-wait hint is shown."""
    return LONG_WAIT_THRESHOLDS.get(model_type.lower(), 300.0)


def human_status_label(status: str | None) -> str:
    """Plain-English label for a Replicate prediction status."""
    if not status:
        return "Starting"
    key = str(status).lower()
    return REPLICATE_STATUS_LABELS.get(key, status.replace("_", " ").title())


def prediction_job_url(prediction: object) -> str:
    """Replicate dashboard URL for a prediction, when available."""
    urls = getattr(prediction, "urls", None)
    if isinstance(urls, dict):
        web = urls.get("web") or urls.get("get")
        if web:
            return str(web)
    return ""


def typical_duration_hint(model_type: str) -> str:
    """Short expectation copy for the generation panel."""
    key = model_type.lower()
    if key == "3d":
        return "typically 1–10 minutes"
    if key == "audio":
        return "typically under a minute"
    if key == "image":
        return "typically 10–90 seconds"
    return "typically 30 seconds to a few minutes"


def format_progress_lines(
    *,
    status: str | None,
    elapsed_seconds: float,
    prediction_id: str = "",
    job_url: str = "",
    model_type: str = "video",
    show_long_wait: bool = False,
) -> tuple[str, str | None]:
    """Build primary progress line and optional long-wait hint."""
    label = human_status_label(status)
    elapsed = format_duration(elapsed_seconds)
    parts = [f"**{label}** · {elapsed} elapsed"]
    if prediction_id:
        parts.append(f"job `{prediction_id}`")
    line = " · ".join(parts)
    if job_url:
        line += f"\n\n[Open job on Replicate]({job_url})"
    long_wait: str | None = None
    if show_long_wait:
        hint = typical_duration_hint(model_type)
        long_wait = (
            "This is taking longer than usual. Replicate may still be queuing or "
            f"working — most {model_type} jobs finish in {hint}. "
            "You can open the job link above to check status on Replicate."
        )
    return line, long_wait


def should_show_long_wait(
    *,
    elapsed_seconds: float,
    status: str | None,
    model_type: str,
) -> bool:
    """True when elapsed time exceeds threshold and job is still in flight."""
    if elapsed_seconds < long_wait_threshold_seconds(model_type):
        return False
    key = (status or "").lower()
    return key in {"starting", "processing"}


class ProgressUpdater:
    """Streamlit-friendly progress callback for Replicate polling."""

    def __init__(
        self,
        progress_line: Any,
        *,
        model_type: str,
        start_time: float | None = None,
    ) -> None:
        self._progress_line = progress_line
        self._model_type = model_type
        self._start_time = start_time if start_time is not None else monotonic()
        self._last_job_url = ""

    def __call__(self, event: str, prediction: object) -> None:
        elapsed = monotonic() - self._start_time
        status = getattr(prediction, "status", event)
        pred_id = str(getattr(prediction, "id", "") or "")
        job_url = prediction_job_url(prediction)
        if job_url:
            self._last_job_url = job_url
        line, long_wait = format_progress_lines(
            status=status,
            elapsed_seconds=elapsed,
            prediction_id=pred_id,
            job_url=job_url or self._last_job_url,
            model_type=self._model_type,
            show_long_wait=should_show_long_wait(
                elapsed_seconds=elapsed,
                status=status,
                model_type=self._model_type,
            ),
        )
        self._progress_line.markdown(line)
        if long_wait:
            self._progress_line.caption(long_wait)
