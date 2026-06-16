"""Unified generation service and dry-run request preparation.

This module is the UI-facing orchestration boundary. Active model wrappers still
own provider execution, output download, and history recording so each workflow
keeps its current model-specific metadata. The service keeps Streamlit tabs from
calling the registry directly and provides a non-paid request-preparation hook
for dry-run / request-preview UI and local probes.
"""

from __future__ import annotations

import json
import logging
from functools import lru_cache
from typing import Any

from src.generation_registry import run_generation, verify_all_models_have_handlers
from src.models_config import ALL_MODELS, ModelConfig, get_model_by_name
from src.pricing import calculate_cost
from src.probe_fixtures import get_probe_kwargs
from src.providers import get_replicate_adapter
from src.replicate_payload import (
    generation_mode_for_payload,
    prepare_payload_for_model,
    summarize_payload_value,
)
from src.schema_diagnostics import compare_model_config, fetch_remote_input_schema
from src.storage_service import StorageService
from src.utils import format_cost, friendly_error_message, sanitize_parameters
from src.validation import ValidationError

logger = logging.getLogger(__name__)


@lru_cache(maxsize=32)
def _cached_latest_version_id(model_id: str) -> str:
    """Return latest Replicate version id for versioned models (no prediction)."""
    return get_replicate_adapter().get_latest_version_id(model_id)


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

        Builds the same Replicate input payload the live handler would send.
        Does not call predictions.create.
        """
        model = get_model_by_name(model_name)
        try:
            payload = prepare_payload_for_model(model, **kwargs)
        except ValidationError as exc:
            return {
                "ok": False,
                "validation_errors": str(exc).splitlines(),
                "model_name": model.name,
            }

        generation_mode = generation_mode_for_payload(model, payload)
        duration = payload.get("duration")
        text_len = sum(
            len(payload[k])
            for k in ("lyrics", "text", "prompt")
            if isinstance(payload.get(k), str)
        )
        if isinstance(duration, (int, float)) and duration > 0:
            pre_cost = calculate_cost(
                model.replicate_id,
                predict_time=0.0,
                output_duration=float(duration),
                text_length=text_len,
            )
            cost_label = format_cost(pre_cost)
        elif text_len > 0 or model.model_type == "audio":
            pre_cost = calculate_cost(
                model.replicate_id,
                predict_time=0.0,
                text_length=text_len,
            )
            cost_label = format_cost(pre_cost) if pre_cost > 0 else (
                model.pricing_notes or "Cost unknown until generation completes"
            )
        else:
            cost_label = "Cost unknown until generation completes"

        endpoint = self._endpoint_summary(model)
        display_payload = {
            key: summarize_payload_value(value) for key, value in payload.items()
        }

        diagnostics = compare_model_config(
            model,
            fetch_remote_input_schema(model.replicate_id),
        )

        return {
            "ok": True,
            "model_name": model.name,
            "display_name": model.display_name,
            "model_type": model.model_type,
            "generation_mode": generation_mode,
            "provider": model.provider,
            "provider_model_id": model.provider_model_id or model.replicate_id,
            "provider_endpoint": model.provider_endpoint,
            "endpoint": endpoint,
            "replicate_page_url": model.replicate_page_url
            or f"https://replicate.com/{model.replicate_id}",
            "metadata_verified_date": model.metadata_verified_date,
            "pricing_notes": model.pricing_notes,
            "output_notes": model.output_notes,
            "multi_output": model.multi_output,
            "estimated_cost_label": cost_label,
            "payload": sanitize_parameters(payload),
            "payload_preview": display_payload,
            "payload_json": json.dumps(display_payload, indent=2, ensure_ascii=False),
            "summary_lines": self._summary_lines(
                model,
                generation_mode,
                endpoint,
                cost_label,
                display_payload,
            ),
            "schema_diagnostics": [
                {
                    "severity": issue.severity,
                    "code": issue.code,
                    "message": issue.message,
                }
                for issue in diagnostics.issues
                if issue.severity != "info"
            ],
        }

    def _endpoint_summary(self, model: ModelConfig) -> dict[str, Any]:
        """Describe how this model would be submitted to Replicate."""
        model_id = model.provider_model_id or model.replicate_id
        if model.provider_endpoint == "versionless":
            return {
                "mode": "versionless",
                "create_call": f'predictions.create(model="{model_id}", input=...)',
                "version_id": None,
            }
        try:
            version_id = _cached_latest_version_id(model_id)
        except Exception as exc:
            return {
                "mode": "versioned",
                "create_call": 'predictions.create(version="<latest>", input=...)',
                "version_id": None,
                "version_lookup_error": str(exc),
            }
        short = f"{version_id[:12]}…" if len(version_id) > 12 else version_id
        return {
            "mode": "versioned",
            "create_call": f'predictions.create(version="{version_id}", input=...)',
            "version_id": version_id,
            "version_id_short": short,
        }

    def _summary_lines(
        self,
        model: ModelConfig,
        generation_mode: str,
        endpoint: dict[str, Any],
        cost_label: str,
        display_payload: dict[str, Any],
    ) -> list[str]:
        """Human-readable dry-run summary lines."""
        param_count = len(display_payload)
        lines = [
            f"Model: {model.display_name} ({model.name})",
            f"Mode: {generation_mode.replace('_', ' ')}",
            f"Provider: {model.provider} · endpoint: {endpoint.get('mode')}",
            f"Estimated cost (pre-run): {cost_label}",
            f"Parameters in payload: {param_count}",
        ]
        if model.pricing_notes:
            lines.append(f"Pricing note: {model.pricing_notes}")
        if endpoint.get("version_id_short"):
            lines.append(f"Latest version: {endpoint['version_id_short']}")
        return lines

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
            return {
                "success": False,
                "error": friendly_error_message(exc),
                "error_detail": str(exc),
            }


_generation_service: UnifiedGenerationService | None = None


def get_generation_service() -> UnifiedGenerationService:
    """Return the lazily-created global generation service."""
    global _generation_service
    if _generation_service is None:
        _generation_service = UnifiedGenerationService()
    return _generation_service


def run_local_safety_checks() -> dict[str, Any]:
    """Non-paid checks: registry, validation probes, optional remote schema."""
    registry_ok = verify_all_models_have_handlers()
    validation_ok = True
    validation_errors: list[str] = []

    for model in ALL_MODELS:
        model_name = model.name
        try:
            prepare_payload_for_model(model, **get_probe_kwargs(model))
        except Exception as exc:
            validation_ok = False
            validation_errors.append(f"{model_name}: {exc}")

    from src.schema_diagnostics import (
        all_reports_ok,
        probe_multimodal_frame_uploads,
        run_all_diagnostics,
    )

    reports = run_all_diagnostics(fetch_remote=True)
    schema_ok = all_reports_ok(reports)

    upload_probe_errors = probe_multimodal_frame_uploads()
    if upload_probe_errors:
        validation_ok = False
        validation_errors.extend(upload_probe_errors)

    return {
        "registry_ok": registry_ok,
        "validation_ok": validation_ok,
        "validation_errors": validation_errors,
        "schema_ok": schema_ok,
        "schema_reports": reports,
    }
