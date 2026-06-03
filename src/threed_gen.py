"""3D generation functions — Hunyuan3D 2.0 and TRELLIS 2.

Pattern identical to video_gen.py:
  build input → run prediction → extract output → cost → record → return.
"""

from __future__ import annotations

import time
from collections.abc import Callable
from functools import lru_cache
from typing import Any

import replicate

from .cost_tracker import record_generation
from .models_config import HUNYUAN3D_2, TRELLIS_2
from .pricing import calculate_cost
from .utils import output_to_url, uploaded_file_metadata
from .validation import validate_params

ProgressCallback = Callable[[str, object], None]


@lru_cache(maxsize=16)
def _latest_version_id(model_id: str) -> str:
    """Return the current latest Replicate version ID for a model slug."""
    model = replicate.models.get(model_id)
    latest_version = getattr(model, "latest_version", None)
    version_id = getattr(latest_version, "id", None)
    if not version_id:
        raise ValueError(f"No latest Replicate version found for {model_id!r}")
    return version_id


def _run_prediction(
    model_id: str,
    input_params: dict,
    progress_callback: ProgressCallback | None = None,
    poll_interval: int = 10,
) -> dict:
    """Create a Replicate prediction, poll, and return normalized output."""
    version_id = _latest_version_id(model_id)
    prediction = replicate.predictions.create(version=version_id, input=input_params)
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

    output = prediction.output
    if isinstance(output, str) or hasattr(output, "url"):
        output = {"mesh": output}

    return {
        "success": True,
        "output": output,
        "predict_time": (prediction.metrics or {}).get("predict_time", 0),
        "total_time": (prediction.metrics or {}).get("total_time", 0),
        "prediction_id": getattr(prediction, "id", ""),
        "prediction_url": getattr(prediction, "urls", {}).get("web", ""),
    }


def _input_image_history_value(image: Any) -> str | None:
    """Return a safe history value for image input without serializing bytes."""
    if isinstance(image, str):
        return image if image.startswith(("http", "data:")) else None
    meta = uploaded_file_metadata(image)
    return meta.get("filename") if meta else None


def generate_hunyuan3d_2(
    image: Any,
    seed: int = 1234,
    steps: int = 50,
    guidance_scale: float = 5.5,
    octree_resolution: int = 256,
    remove_background: bool = True,
    progress_callback: ProgressCallback | None = None,
) -> dict:
    """Hunyuan3D 2.0 — Image-to-3D mesh generation."""
    model = HUNYUAN3D_2
    input_params: dict[str, Any] = {
        "image": image,
        "seed": seed,
        "steps": steps,
        "guidance_scale": guidance_scale,
        "octree_resolution": octree_resolution,
        "remove_background": remove_background,
    }

    validate_params(model, input_params)
    result = _run_prediction(model.replicate_id, input_params, progress_callback)
    if result["success"]:
        mesh_url = output_to_url(result["output"].get("mesh", result["output"]))
        cost = calculate_cost(model.replicate_id, result["predict_time"])
        record_generation(
            model_name=model.name,
            model_type="3d",
            prompt="",
            parameters=input_params,
            replicate_url=mesh_url,
            predict_time=result["predict_time"],
            total_time=result["total_time"],
            estimated_cost=cost,
            generation_mode="image_to_3d",
            input_image_path=_input_image_history_value(image),
        )
        result["mesh_url"] = mesh_url
        result["estimated_cost"] = cost
    return result


def generate_trellis_2(
    image: Any,
    seed: int = 42,
    pipeline_type: str = "1024_cascade",
    generate_model: bool = True,
    generate_video: bool = True,
    texture_size: int = 4096,
    decimation_target: int = 1_000_000,
    preprocess_image: bool = True,
    sparse_structure_steps: int = 12,
    shape_slat_steps: int = 12,
    tex_slat_steps: int = 12,
    shape_slat_guidance_strength: float = 7.5,
    tex_slat_guidance_strength: float = 1.0,
    progress_callback: ProgressCallback | None = None,
) -> dict:
    """TRELLIS 2 — Image-to-3D with PBR textures and optional video preview."""
    model = TRELLIS_2
    input_params: dict[str, Any] = {
        "image": image,
        "seed": seed,
        "pipeline_type": pipeline_type,
        "generate_model": generate_model,
        "generate_video": generate_video,
        "texture_size": texture_size,
        "decimation_target": decimation_target,
        "preprocess_image": preprocess_image,
        "sparse_structure_steps": sparse_structure_steps,
        "shape_slat_steps": shape_slat_steps,
        "tex_slat_steps": tex_slat_steps,
        "shape_slat_guidance_strength": shape_slat_guidance_strength,
        "tex_slat_guidance_strength": tex_slat_guidance_strength,
    }

    validate_params(model, input_params)
    result = _run_prediction(model.replicate_id, input_params, progress_callback)
    if result["success"]:
        output = result["output"]
        model_url = output_to_url(output.get("model_file", output))
        video_url = output_to_url(output.get("video", ""))
        cost = calculate_cost(model.replicate_id, result["predict_time"])
        record_generation(
            model_name=model.name,
            model_type="3d",
            prompt="",
            parameters=input_params,
            replicate_url=model_url,
            predict_time=result["predict_time"],
            total_time=result["total_time"],
            estimated_cost=cost,
            generation_mode="image_to_3d",
            input_image_path=_input_image_history_value(image),
        )
        result["model_url"] = model_url
        result["video_url"] = video_url
        result["estimated_cost"] = cost
    return result
