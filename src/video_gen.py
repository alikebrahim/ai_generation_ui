"""Video generation functions — one per model, all sharing a common pattern.

Each function:
  1. Builds the Replicate input dict from user parameters
  2. Creates a prediction, polls until complete
  3. Extracts output URL + metrics
  4. Calculates estimated cost
  5. Records the generation in SQLite history
  6. Returns a uniform result dict
"""

from __future__ import annotations

import time
from collections.abc import Callable
from typing import Any

import replicate

from .cost_tracker import record_generation
from .models_config import SEEDANCE_2_0, WAN_2_5_I2V, WAN_2_7_T2V
from .pricing import calculate_cost
from .utils import output_to_url, uploaded_file_metadata
from .validation import validate_params

ProgressCallback = Callable[[str, object], None]


def _input_image_history_value(image: Any) -> str | None:
    """Return a safe history value for image input without serializing bytes."""
    if isinstance(image, str):
        return image if image.startswith(("http", "data:")) else None
    meta = uploaded_file_metadata(image)
    return meta.get("filename") if meta else None


def _run_prediction(
    model_id: str,
    input_params: dict,
    progress_callback: ProgressCallback | None = None,
    poll_interval: int = 5,
) -> dict:
    """Create a Replicate prediction, poll it, and return a normalized result."""
    prediction = replicate.predictions.create(model=model_id, input=input_params)
    if progress_callback:
        progress_callback("created", prediction)

    while prediction.status not in ("succeeded", "failed", "canceled"):
        time.sleep(poll_interval)
        prediction = replicate.predictions.get(prediction.id)
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
    input_params: dict[str, Any] = {
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "enable_prompt_expansion": enable_prompt_expansion,
    }
    if seed is not None and seed >= 0:
        input_params["seed"] = seed
    if negative_prompt:
        input_params["negative_prompt"] = negative_prompt
    if audio:
        input_params["audio"] = audio

    validate_params(model, input_params)
    result = _run_prediction(model.replicate_id, input_params, progress_callback)
    if result["success"]:
        cost = calculate_cost(
            model.replicate_id,
            result["predict_time"],
            output_duration=duration,
        )
        record_generation(
            model_name=model.name,
            model_type="video",
            prompt=prompt,
            parameters=input_params,
            replicate_url=result["url"],
            predict_time=result["predict_time"],
            total_time=result["total_time"],
            estimated_cost=cost,
            output_duration=duration,
            generation_mode="text_to_video",
        )
        result["estimated_cost"] = cost
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
    input_params: dict[str, Any] = {
        "prompt": prompt,
        "image": image,
        "duration": duration,
        "resolution": resolution,
        "enable_prompt_expansion": enable_prompt_expansion,
    }
    if seed is not None and seed >= 0:
        input_params["seed"] = seed
    if negative_prompt:
        input_params["negative_prompt"] = negative_prompt
    if audio:
        input_params["audio"] = audio

    validate_params(model, input_params)
    result = _run_prediction(model.replicate_id, input_params, progress_callback)
    if result["success"]:
        cost = calculate_cost(
            model.replicate_id,
            result["predict_time"],
            output_duration=duration,
        )
        record_generation(
            model_name=model.name,
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
        )
        result["estimated_cost"] = cost
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
    input_params: dict[str, Any] = {
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "generate_audio": generate_audio,
    }
    if seed is not None and seed >= 0:
        input_params["seed"] = seed
    if image:
        input_params["image"] = image
    if last_frame_image:
        input_params["last_frame_image"] = last_frame_image
    if reference_images:
        input_params["reference_images"] = reference_images
    if reference_videos:
        input_params["reference_videos"] = reference_videos
    if reference_audios:
        input_params["reference_audios"] = reference_audios

    validate_params(model, input_params)
    result = _run_prediction(model.replicate_id, input_params, progress_callback)
    if result["success"]:
        cost = calculate_cost(
            model.replicate_id,
            result["predict_time"],
            output_duration=duration,
        )
        history_params = {
            k: v
            for k, v in input_params.items()
            if k
            not in (
                "reference_images",
                "reference_videos",
                "reference_audios",
            )
        }
        record_generation(
            model_name=model.name,
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
        )
        result["estimated_cost"] = cost
    return result
