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

    probe_file = {"name": "probe.png", "type": "image/png", "size": 100}
    probe_obj = {"name": "probe.obj", "type": "model/obj", "size": 100}
    for model in ALL_MODELS:
        model_name = model.name
        try:
            if model.name == "wan-2.7-t2v":
                prepare_payload_for_model(
                    model, prompt="probe", duration=5, resolution="1080p"
                )
            elif model.name == "wan-2.5-i2v-fast":
                prepare_payload_for_model(
                    model,
                    prompt="probe",
                    image=probe_file,
                    duration=5,
                )
            elif model.name == "seedance-2.0":
                prepare_payload_for_model(model, prompt="probe", duration=5)
            elif model.name == "happyhorse-1.0":
                prepare_payload_for_model(
                    model,
                    prompt="probe",
                    duration=5,
                    resolution="720p",
                    _generation_mode="text",
                )
            elif model.name == "gen-4.5":
                prepare_payload_for_model(model, prompt="probe", duration=5)
            elif model.name == "seedance-2.0-fast":
                prepare_payload_for_model(model, prompt="probe", duration=5)
            elif model.name == "kling-v3-omni":
                prepare_payload_for_model(
                    model, prompt="probe", duration=5, mode="standard"
                )
            elif model.name == "dreamactor-m2.0":
                prepare_payload_for_model(
                    model, image=probe_file, video=probe_file
                )
            elif model.name == "aleph-2":
                prepare_payload_for_model(
                    model, prompt="probe edit", video=probe_file
                )
            elif model.name == "kling-v3-motion":
                prepare_payload_for_model(
                    model,
                    image=probe_file,
                    video=probe_file,
                    mode="std",
                )
            elif model.name == "kling-o1":
                prepare_payload_for_model(model, prompt="probe", duration=5)
            elif model.name == "hunyuan-3d-3.1":
                prepare_payload_for_model(model, prompt="probe chair")
            elif model.name == "text2tex":
                prepare_payload_for_model(
                    model, prompt="red fabric", obj_file=probe_obj
                )
            elif model.name == "adirik-texture":
                prepare_payload_for_model(
                    model, prompt="wood grain", shape_path=probe_obj
                )
            elif model.name == "rodin":
                prepare_payload_for_model(model, prompt="a wooden chair")
            elif model.name == "hunyuan3d-2mv":
                prepare_payload_for_model(model, front_image=probe_file)
            elif model.name == "music-2.5":
                prepare_payload_for_model(model, lyrics="verse one\nchorus")
            elif model.name == "stable-audio-2.5":
                prepare_payload_for_model(
                    model, prompt="ambient pad", duration=5
                )
            elif model.name == "lyria-2":
                prepare_payload_for_model(model, prompt="calm piano")
            elif model.name in (
                "realtime-tts-2",
                "realtime-tts-1.5-max",
                "speech-2.8-hd",
                "speech-2.8-turbo",
            ):
                prepare_payload_for_model(model, text="Hello, this is a test.")
            elif model.name == "chatterbox":
                prepare_payload_for_model(model, prompt="Hello world")
            elif model.name == "elevenlabs-v3":
                prepare_payload_for_model(model, prompt="Hello world")
            else:
                prepare_payload_for_model(model, image=probe_file)
        except Exception as exc:
            validation_ok = False
            validation_errors.append(f"{model_name}: {exc}")

    from src.schema_diagnostics import all_reports_ok, run_all_diagnostics

    reports = run_all_diagnostics(fetch_remote=True)
    schema_ok = all_reports_ok(reports)

    return {
        "registry_ok": registry_ok,
        "validation_ok": validation_ok,
        "validation_errors": validation_errors,
        "schema_ok": schema_ok,
        "schema_reports": reports,
    }
