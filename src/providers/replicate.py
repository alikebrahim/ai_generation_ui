"""Replicate provider adapter — isolates SDK-specific details."""

from __future__ import annotations

import os
import time
from collections.abc import Callable
from typing import Any

import replicate
from replicate.exceptions import ReplicateError

from src.generation_progress import prediction_job_url
from src.providers.base import ProviderAdapter
from src.utils import friendly_error_message, output_to_url, technical_error_detail

ProgressCallback = Callable[[str, object], None]

_TERMINAL_STATUSES = frozenset({"succeeded", "failed", "canceled"})


class ReplicateAdapter(ProviderAdapter):
    """Adapter for Replicate API."""

    def check_credential_status(self) -> bool:
        """Return True if REPLICATE_API_TOKEN is set."""
        return bool(os.getenv("REPLICATE_API_TOKEN"))

    def create_prediction(
        self,
        model_id: str,
        version_id: str | None,
        input_params: dict[str, Any],
    ) -> Any:
        """Create a prediction using versionless or versioned endpoint."""
        if version_id:
            return replicate.predictions.create(
                version=version_id,
                input=input_params,
            )
        return replicate.predictions.create(
            model=model_id,
            input=input_params,
        )

    def poll_prediction(self, prediction: Any) -> Any:
        """Poll Replicate API for prediction status."""
        return replicate.predictions.get(prediction.id)

    def wait_for_prediction(
        self,
        prediction: Any,
        *,
        poll_interval: int = 5,
        progress_callback: ProgressCallback | None = None,
    ) -> Any:
        """Poll until the prediction reaches a terminal status."""
        if progress_callback:
            progress_callback("created", prediction)
        while prediction.status not in _TERMINAL_STATUSES:
            time.sleep(poll_interval)
            prediction = self.poll_prediction(prediction)
            if progress_callback:
                progress_callback("polled", prediction)
        return prediction

    def normalize_output(self, prediction: Any, output_key: str = "output") -> Any:
        """Extract and normalize output from Replicate prediction."""
        if not hasattr(prediction, "output") or prediction.output is None:
            return None
        return output_to_url(prediction.output)

    def friendly_error_message(self, error: Any) -> str:
        """Format Replicate error for user display."""
        if isinstance(error, ReplicateError):
            return friendly_error_message(error)
        return friendly_error_message(str(error))

    def prediction_failure_message(self, prediction: Any) -> str:
        """User-facing message when a prediction ends in failed/canceled."""
        status = getattr(prediction, "status", "failed")
        raw = getattr(prediction, "error", None) or f"Status: {status}"
        return self.friendly_error_message(raw)

    def prediction_result_dict(
        self,
        prediction: Any,
        *,
        success_output: Any | None = None,
    ) -> dict[str, Any]:
        """Normalize a terminal prediction into the app's result dict shape."""
        pred_id = getattr(prediction, "id", "")
        job_url = prediction_job_url(prediction)
        metrics = prediction.metrics or {}
        base = {
            "prediction_id": pred_id,
            "prediction_url": job_url,
            "predict_time": metrics.get("predict_time", 0),
            "total_time": metrics.get("total_time", 0),
        }
        if prediction.status == "succeeded" and success_output is not None:
            return {"success": True, **base, **success_output}
        raw_error = getattr(prediction, "error", None) or f"Status: {prediction.status}"
        return {
            "success": False,
            "error": self.prediction_failure_message(prediction),
            "error_detail": technical_error_detail(str(raw_error)) or str(raw_error),
            **base,
        }

    def get_latest_version_id(self, model_id: str) -> str:
        """Fetch latest version ID for a Replicate model."""
        model = replicate.models.get(model_id)
        if not model or not hasattr(model, "latest_version"):
            raise RuntimeError(
                f"Could not fetch latest version for {model_id}. "
                f"Verify the model exists and you have permission."
            )
        return model.latest_version.id


_replicate_adapter = ReplicateAdapter()


def get_replicate_adapter() -> ReplicateAdapter:
    """Return the global Replicate adapter instance."""
    return _replicate_adapter
