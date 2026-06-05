"""Audio generation — music and speech via Replicate."""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import Any

from src.audio_payload import AUDIO_PAYLOAD_BUILDERS
from src.cost_tracker import record_generation
from src.models_config import get_model_by_name
from src.pricing import calculate_cost
from src.providers import get_replicate_adapter
from src.replicate_payload import generation_mode_for_payload
from src.storage_service import get_storage_service
from src.utils import output_to_url, sanitize_parameters
from src.validation import validate_params

ProgressCallback = Callable[[str, object], None]


def _run_prediction(
    model_id: str,
    input_params: dict,
    progress_callback: ProgressCallback | None = None,
    poll_interval: int = 5,
) -> dict:
    adapter = get_replicate_adapter()
    prediction = adapter.create_prediction(model_id, None, input_params)
    prediction = adapter.wait_for_prediction(
        prediction,
        poll_interval=poll_interval,
        progress_callback=progress_callback,
    )
    if prediction.status != "succeeded":
        return adapter.prediction_result_dict(prediction)
    return adapter.prediction_result_dict(
        prediction,
        success_output={"url": output_to_url(prediction.output)},
    )


def _primary_text_for_history(payload: dict[str, Any]) -> str:
    for key in ("lyrics", "text", "prompt"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def _serialize_audio_assets(primary_url: str, local: dict[str, Any]) -> str:
    payload = [
        {
            "kind": "audio",
            "provider_url": primary_url,
            "local_path": local.get("local_path"),
            "file_size_bytes": local.get("file_size_bytes"),
            "mime_type": local.get("mime_type") or "audio/mpeg",
        }
    ]
    return json.dumps(payload, ensure_ascii=False)


def generate_audio_model(
    model_name: str,
    progress_callback: ProgressCallback | None = None,
    **kwargs: Any,
) -> dict:
    """Run any configured audio model through the shared prediction pipeline."""
    if model_name not in AUDIO_PAYLOAD_BUILDERS:
        raise ValueError(f"No audio handler for model: {model_name!r}")
    model = get_model_by_name(model_name)
    builder = AUDIO_PAYLOAD_BUILDERS[model_name]
    input_params = builder(**kwargs)
    validate_params(model, input_params)
    result = _run_prediction(model.replicate_id, input_params, progress_callback)
    if result.get("success"):
        cost = calculate_cost(
            model.replicate_id,
            result.get("predict_time", 0),
            text_length=_billing_text_length(input_params),
            output_duration=float(input_params.get("duration") or 0),
        )
        local = get_storage_service().download_output(
            result["url"],
            "audio",
            prefix="audio",
        )
        history_params = sanitize_parameters(input_params)
        assets_json = _serialize_audio_assets(result["url"], local)
        prompt = _primary_text_for_history(input_params)
        record_generation(
            model_name=model.name,
            provider=model.provider,
            provider_model_id=model.provider_model_id or model.replicate_id,
            provider_job_id=result.get("prediction_id"),
            provider_job_url=result.get("prediction_url"),
            model_type="audio",
            prompt=prompt,
            parameters=history_params,
            replicate_url=result["url"],
            predict_time=result.get("predict_time", 0),
            total_time=result.get("total_time", 0),
            estimated_cost=cost,
            generation_mode=generation_mode_for_payload(model, input_params),
            local_file_path=local.get("local_path"),
            file_size_bytes=local.get("file_size_bytes"),
            output_assets_json=assets_json,
        )
        result["local_file_path"] = local.get("local_path")
        result["file_size_bytes"] = local.get("file_size_bytes")
        result["estimated_cost"] = cost
        result["output_assets_json"] = assets_json
    return result


def _billing_text_length(payload: dict[str, Any]) -> int:
    total = 0
    for key in ("lyrics", "text", "prompt"):
        val = payload.get(key)
        if isinstance(val, str):
            total += len(val)
    return total
