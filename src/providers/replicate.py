"""Replicate provider adapter — isolates SDK-specific details."""

from __future__ import annotations

import os
from typing import Any

import replicate

from src.providers.base import ProviderAdapter
from src.utils import friendly_error_message, output_to_url


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
            # Versioned endpoint for models requiring it (e.g., Hunyuan3D 2)
            return replicate.predictions.create(
                version=version_id,
                input=input_params,
            )
        else:
            # Versionless endpoint (default)
            return replicate.predictions.create(
                model=model_id,
                input=input_params,
            )

    def poll_prediction(self, prediction: Any) -> Any:
        """Poll Replicate API for prediction status."""
        return replicate.predictions.get(prediction.id)

    def normalize_output(self, prediction: Any, output_key: str = "output") -> Any:
        """Extract and normalize output from Replicate prediction."""
        if not hasattr(prediction, "output") or prediction.output is None:
            return None
        return output_to_url(prediction.output)

    def friendly_error_message(self, error: Any) -> str:
        """Format Replicate error for user display."""
        return friendly_error_message(error)

    def get_latest_version_id(self, model_id: str) -> str:
        """Fetch latest version ID for a Replicate model.

        Used for models that require versioned prediction endpoint.
        """
        model = replicate.models.get(model_id)
        if not model or not hasattr(model, "latest_version"):
            raise RuntimeError(
                f"Could not fetch latest version for {model_id}. "
                f"Verify the model exists and you have permission."
            )
        return model.latest_version.id


# Global singleton instance
_replicate_adapter = ReplicateAdapter()


def get_replicate_adapter() -> ReplicateAdapter:
    """Return the global Replicate adapter instance."""
    return _replicate_adapter
