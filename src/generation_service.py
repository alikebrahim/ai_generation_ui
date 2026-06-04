"""Unified generation service and dry-run request preparation.

This module is the UI-facing orchestration boundary. Active model wrappers still
own provider execution, output download, and history recording so each workflow
keeps its current model-specific metadata. The service keeps Streamlit tabs from
calling the registry directly and provides a non-paid request-preparation hook
for the v0.5 dry-run UI.
"""

from __future__ import annotations

import logging
from typing import Any

from src.generation_registry import run_generation
from src.models_config import get_model_by_name
from src.storage_service import StorageService
from src.utils import sanitize_parameters
from src.validation import validate_params

logger = logging.getLogger(__name__)


class UnifiedGenerationService:
    """Coordinates UI requests with generation handlers and dry-run prep."""

    def __init__(self, storage: StorageService | None = None):
        """Initialize the service without touching provider APIs."""
        self.storage = storage or StorageService()

    def prepare_generation_request(
        self,
        model_name: str,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Validate and summarize a generation request without a paid API call.

        This deliberately does not call Replicate. It is a stable hook for the
        v0.5 dry-run/request-preview UI and for local probes.
        """
        model = get_model_by_name(model_name)
        payload = {
            key: value
            for key, value in kwargs.items()
            if key not in {"progress_callback", "_uploaded_image"}
        }
        validate_params(model, payload)
        return {
            "model_name": model.name,
            "model_type": model.model_type,
            "provider": model.provider,
            "provider_model_id": model.provider_model_id or model.replicate_id,
            "provider_endpoint": model.provider_endpoint,
            "payload": sanitize_parameters(payload),
        }

    def generate(
        self,
        model_name: str,
        model_type: str | None = None,
        **kwargs: Any,
    ) -> dict[str, Any]:
        """Execute a generation workflow through the registry.

        History is recorded inside the concrete generation handlers. Keeping one
        write owner avoids duplicate history rows while the app remains
        Replicate-only through v0.4.9.
        """
        try:
            _ = model_type  # Kept for a stable UI call signature.
            result = run_generation(model_name, **kwargs)
            return result or {"success": False, "error": "No result returned"}
        except Exception as exc:
            logger.exception("Generation workflow error for %s: %s", model_name, exc)
            return {"success": False, "error": str(exc)}


_generation_service: UnifiedGenerationService | None = None


def get_generation_service() -> UnifiedGenerationService:
    """Return the lazily-created global generation service."""
    global _generation_service
    if _generation_service is None:
        _generation_service = UnifiedGenerationService()
    return _generation_service
