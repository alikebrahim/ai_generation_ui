"""Provider adapter base protocol."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class ProviderAdapter(ABC):
    """Base adapter for generation providers (Replicate, fal.ai, etc)."""

    @abstractmethod
    def check_credential_status(self) -> bool:
        """Return True if provider credentials are available."""
        pass

    @abstractmethod
    def create_prediction(
        self,
        model_id: str,
        version_id: str | None,
        input_params: dict[str, Any],
    ) -> Any:
        """Create a prediction on the provider."""
        pass

    @abstractmethod
    def poll_prediction(self, prediction: Any) -> Any:
        """Poll for prediction status; return updated prediction."""
        pass

    @abstractmethod
    def normalize_output(self, prediction: Any, output_key: str = "output") -> Any:
        """Extract and normalize output from a completed prediction."""
        pass

    @abstractmethod
    def friendly_error_message(self, error: Any) -> str:
        """Format provider-specific error for user display."""
        pass
