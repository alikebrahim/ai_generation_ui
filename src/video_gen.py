"""Video generation functions — one per model, all sharing a common pattern.

Each function:
  1. Builds the Replicate input dict from user parameters
  2. Creates a prediction, polls until complete
  3. Extracts output URL + metrics
  4. Calculates estimated cost
  5. Downloads outputs locally when possible
  6. Records the generation in SQLite history
  7. Returns a uniform result dict
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from typing import Any

from src.cost_tracker import record_generation
from src.models_config import SEEDANCE_2_0, WAN_2_5_I2V, WAN_2_7_T2V, get_model_by_name
from src.pricing import calculate_cost
from src.providers import get_replicate_adapter
from src.replicate_payload import (
    build_replicate_input,
    build_seedance_2_0_input,
    build_wan_2_5_i2v_input,
    build_wan_2_7_t2v_input,
    generation_mode_for_payload,
)
from src.storage_service import get_storage_service
from src.utils import output_to_url, uploaded_file_metadata
from src.validation import validate_params

ProgressCallback = Callable[[str, object], None]


def _input_image_history_value(image: Any) -> str | None:
    """Return a safe history value for image input without serializing bytes."""
    if isinstance(image, str):
        return image if image.startswith(("http", "data:")) else None
    meta = uploaded_file_metadata(image)
    return meta.get("filename") if meta else None


def _serialize_video_assets(primary_url: str, local: dict[str, Any]) -> str:
    """Serialize video output assets for history storage."""
    payload = [
        {
            "kind": "video",
            "provider_url": primary_url,
            "local_path": local.get("local_path"),
            "thumbnail_path": local.get("thumbnail_path"),
            "file_size_bytes": local.get("file_size_bytes"),
            "mime_type": "video/mp4",
        }
    ]
    return json.dumps(payload, ensure_ascii=False)


def _run_prediction(
    model_id: str,
    input_params: dict,
    progress_callback: ProgressCallback | None = None,
    poll_interval: int = 5,
) -> dict:
    """Create a Replicate prediction, poll it, and return a normalized result."""
    adapter = get_replicate_adapter()
    prediction = adapter.create_prediction(model_id, None, input_params)
    if progress_callback:
        progress_callback("created", prediction)

    while prediction.status not in ("succeeded", "failed", "canceled"):
        time.sleep(poll_interval)
        prediction = adapter.poll_prediction(prediction)
        if progress_callback:
            progress_callback("polled", prediction)

    if prediction.status != "succeeded":
        return {
            "success": False,
            "error": prediction.error or f"Status: {prediction.status}",
            "prediction_id": getattr(prediction, "id", ""),
            "prediction_url": getattr(prediction, "urls", {}).get("web", ""),
        }

    return {
        "success": True,
        "url": output_to_url(prediction.output),
        "predict_time": (prediction.metrics or {}).get("predict_time", 0),
        "total_time": (prediction.metrics or {}).get("total_time", 0),
        "prediction_id": getattr(prediction, "id", ""),
        "prediction_url": getattr(prediction, "urls", {}).get("web", ""),
    }


def generate_wan_2_7_t2v(
    prompt: str,
    duration: int = 5,
    resolution: str = "1080p",
    aspect_ratio: str = "16:9",
    seed: int | None = None,
    negative_prompt: str = "",
    enable_prompt_expansion: bool = True,
    audio: str | None = None,
    progress_callback: ProgressCallback | None = None,
) -> dict:
    """Wan 2.7 Text-to-Video."""
    model = WAN_2_7_T2V
    input_params = build_wan_2_7_t2v_input(
        prompt=prompt,
        duration=duration,
        resolution=resolution,
        aspect_ratio=aspect_ratio,
        seed=seed,
        negative_prompt=negative_prompt,
        enable_prompt_expansion=enable_prompt_expansion,
        audio=audio,
    )
    validate_params(model, input_params)
    result = _run_prediction(model.replicate_id, input_params, progress_callback)
    if result["success"]:
        cost = calculate_cost(
            model.replicate_id,
            result["predict_time"],
            output_duration=duration,
        )
        local = get_storage_service().download_output(
            result["url"],
            "video",
            prefix="video",
        )
        assets_json = _serialize_video_assets(result["url"], local)
        record_generation(
            model_name=model.name,
            provider=model.provider,
            provider_model_id=model.provider_model_id or model.replicate_id,
            provider_job_id=result.get("prediction_id"),
            provider_job_url=result.get("prediction_url"),
            model_type="video",
            prompt=prompt,
            parameters=input_params,
            replicate_url=result["url"],
            predict_time=result["predict_time"],
            total_time=result["total_time"],
            estimated_cost=cost,
            output_duration=duration,
            generation_mode="text_to_video",
            local_file_path=local.get("local_path"),
            thumbnail_path=local.get("thumbnail_path"),
            file_size_bytes=local.get("file_size_bytes"),
            output_assets_json=assets_json,
        )
        result["local_file_path"] = local.get("local_path")
        result["thumbnail_path"] = local.get("thumbnail_path")
        result["file_size_bytes"] = local.get("file_size_bytes")
        result["estimated_cost"] = cost
        result["output_assets_json"] = assets_json
    return result


def generate_wan_2_5_i2v(
    prompt: str,
    image: Any,
    duration: int = 5,
    resolution: str = "720p",
    seed: int | None = None,
    negative_prompt: str = "",
    enable_prompt_expansion: bool = True,
    audio: str | None = None,
    progress_callback: ProgressCallback | None = None,
) -> dict:
    """Wan 2.5 Image-to-Video Fast."""
    model = WAN_2_5_I2V
    input_params = build_wan_2_5_i2v_input(
        prompt=prompt,
        image=image,
        duration=duration,
        resolution=resolution,
        seed=seed,
        negative_prompt=negative_prompt,
        enable_prompt_expansion=enable_prompt_expansion,
        audio=audio,
    )
    validate_params(model, input_params)
    result = _run_prediction(model.replicate_id, input_params, progress_callback)
    if result["success"]:
        cost = calculate_cost(
            model.replicate_id,
            result["predict_time"],
            output_duration=duration,
        )
        local = get_storage_service().download_output(
            result["url"],
            "video",
            prefix="video",
        )
        assets_json = _serialize_video_assets(result["url"], local)
        record_generation(
            model_name=model.name,
            provider=model.provider,
            provider_model_id=model.provider_model_id or model.replicate_id,
            provider_job_id=result.get("prediction_id"),
            provider_job_url=result.get("prediction_url"),
            model_type="video",
            prompt=prompt,
            parameters=input_params,
            replicate_url=result["url"],
            predict_time=result["predict_time"],
            total_time=result["total_time"],
            estimated_cost=cost,
            output_duration=duration,
            generation_mode="image_to_video",
            input_image_path=_input_image_history_value(image),
            local_file_path=local.get("local_path"),
            thumbnail_path=local.get("thumbnail_path"),
            file_size_bytes=local.get("file_size_bytes"),
            output_assets_json=assets_json,
        )
        result["local_file_path"] = local.get("local_path")
        result["thumbnail_path"] = local.get("thumbnail_path")
        result["file_size_bytes"] = local.get("file_size_bytes")
        result["estimated_cost"] = cost
        result["output_assets_json"] = assets_json
    return result


def generate_seedance_2_0(
    prompt: str,
    duration: int = 5,
    resolution: str = "720p",
    aspect_ratio: str = "16:9",
    seed: int | None = None,
    generate_audio: bool = True,
    image: Any | None = None,
    last_frame_image: Any | None = None,
    reference_images: list[str] | None = None,
    reference_videos: list[str] | None = None,
    reference_audios: list[str] | None = None,
    progress_callback: ProgressCallback | None = None,
) -> dict:
    """Seedance 2.0 — T2V or I2V with optional multi-reference inputs."""
    model = SEEDANCE_2_0
    input_params = build_seedance_2_0_input(
        prompt=prompt,
        duration=duration,
        resolution=resolution,
        aspect_ratio=aspect_ratio,
        seed=seed,
        generate_audio=generate_audio,
        image=image,
        last_frame_image=last_frame_image,
        reference_images=reference_images,
        reference_videos=reference_videos,
        reference_audios=reference_audios,
    )
    validate_params(model, input_params)
    result = _run_prediction(model.replicate_id, input_params, progress_callback)
    if result["success"]:
        cost = calculate_cost(
            model.replicate_id,
            result["predict_time"],
            output_duration=duration,
        )
        local = get_storage_service().download_output(
            result["url"],
            "video",
            prefix="video",
        )
        history_params = {
            k: v
            for k, v in input_params.items()
            if k not in ("reference_images", "reference_videos", "reference_audios")
        }
        assets_json = _serialize_video_assets(result["url"], local)
        record_generation(
            model_name=model.name,
            provider=model.provider,
            provider_model_id=model.provider_model_id or model.replicate_id,
            provider_job_id=result.get("prediction_id"),
            provider_job_url=result.get("prediction_url"),
            model_type="video",
            prompt=prompt,
            parameters=history_params,
            replicate_url=result["url"],
            predict_time=result["predict_time"],
            total_time=result["total_time"],
            estimated_cost=cost,
            output_duration=duration,
            generation_mode="image_to_video" if image else "text_to_video",
            input_image_path=_input_image_history_value(image),
            local_file_path=local.get("local_path"),
            thumbnail_path=local.get("thumbnail_path"),
            file_size_bytes=local.get("file_size_bytes"),
            output_assets_json=assets_json,
        )
        result["local_file_path"] = local.get("local_path")
        result["thumbnail_path"] = local.get("thumbnail_path")
        result["file_size_bytes"] = local.get("file_size_bytes")
        result["estimated_cost"] = cost
        result["output_assets_json"] = assets_json
    return result


def _billing_duration(input_params: dict[str, Any]) -> float:
    """Duration used for output-based cost estimates."""
    duration = input_params.get("duration")
    if isinstance(duration, (int, float)) and duration > 0:
        return float(duration)
    return 5.0


def _history_parameters(input_params: dict[str, Any]) -> dict[str, Any]:
    """Omit bulky file/list blobs from stored generation parameters."""
    skip_keys = {
        "reference_images",
        "reference_videos",
        "reference_audios",
        "keyframe_images",
        "keyframe_positions",
    }
    return {k: v for k, v in input_params.items() if k not in skip_keys}


def generate_video_model(
    model_name: str,
    progress_callback: ProgressCallback | None = None,
    **kwargs: Any,
) -> dict:
    """Run any configured video model through the shared prediction pipeline."""
    model = get_model_by_name(model_name)
    input_params = build_replicate_input(model_name, **kwargs)
    validate_params(model, input_params)
    result = _run_prediction(model.replicate_id, input_params, progress_callback)
    if result["success"]:
        bill_duration = _billing_duration(input_params)
        cost = calculate_cost(
            model.replicate_id,
            result["predict_time"],
            output_duration=bill_duration,
        )
        local = get_storage_service().download_output(
            result["url"],
            "video",
            prefix="video",
        )
        history_params = _history_parameters(input_params)
        assets_json = _serialize_video_assets(result["url"], local)
        prompt = str(input_params.get("prompt") or "")
        record_generation(
            model_name=model.name,
            provider=model.provider,
            provider_model_id=model.provider_model_id or model.replicate_id,
            provider_job_id=result.get("prediction_id"),
            provider_job_url=result.get("prediction_url"),
            model_type="video",
            prompt=prompt,
            parameters=history_params,
            replicate_url=result["url"],
            predict_time=result["predict_time"],
            total_time=result["total_time"],
            estimated_cost=cost,
            output_duration=bill_duration,
            generation_mode=generation_mode_for_payload(model, input_params),
            input_image_path=_input_image_history_value(
                input_params.get("image") or input_params.get("start_image")
            ),
            local_file_path=local.get("local_path"),
            thumbnail_path=local.get("thumbnail_path"),
            file_size_bytes=local.get("file_size_bytes"),
            output_assets_json=assets_json,
        )
        result["local_file_path"] = local.get("local_path")
        result["thumbnail_path"] = local.get("thumbnail_path")
        result["file_size_bytes"] = local.get("file_size_bytes")
        result["estimated_cost"] = cost
        result["output_assets_json"] = assets_json
    return result


def _register_v06_video_handlers() -> dict[str, Callable[..., dict]]:
    """Handlers for v0.6.10 video models."""
    slugs = [
        "happyhorse-1.0",
        "gen-4.5",
        "seedance-2.0-fast",
        "kling-v3-omni",
        "dreamactor-m2.0",
        "aleph-2",
        "kling-v3-motion",
        "kling-o1",
    ]
    handlers: dict[str, Callable[..., dict]] = {}

    def _make(slug: str) -> Callable[..., dict]:
        def _run(progress_callback: ProgressCallback | None = None, **kw: Any) -> dict:
            return generate_video_model(
                slug, progress_callback=progress_callback, **kw
            )

        return _run

    for slug in slugs:
        handlers[slug] = _make(slug)
    return handlers


V06_VIDEO_HANDLERS = _register_v06_video_handlers()
