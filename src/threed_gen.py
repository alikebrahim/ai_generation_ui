"""3D generation functions — Hunyuan3D 2.0, Hunyuan 3D 3.1, and TRELLIS 2.

Pattern identical to video_gen.py:
  build input → run prediction → extract output → cost → record → return.
"""

from __future__ import annotations

import json
import time
from collections.abc import Callable
from functools import lru_cache
from typing import Any

from src.cost_tracker import record_generation
from src.models_config import HUNYUAN3D_2, HUNYUAN_3D_3_1, TRELLIS_2
from src.pricing import calculate_cost
from src.providers import get_replicate_adapter
from src.storage_service import get_storage_service
from src.utils import image_to_data_uri, output_to_url, uploaded_file_metadata
from src.validation import validate_params

ProgressCallback = Callable[[str, object], None]


def _serialize_3d_assets(
    primary_url: str, local: dict[str, Any], preview: dict[str, Any] | None = None
) -> str:
    """Serialize 3D output assets for history storage."""
    payload: list[dict[str, Any]] = [
        {
            "kind": "model",
            "provider_url": primary_url,
            "local_path": local.get("local_path"),
            "thumbnail_path": local.get("thumbnail_path"),
            "file_size_bytes": local.get("file_size_bytes"),
            "mime_type": "model/gltf-binary",
        }
    ]
    if preview:
        payload.append(
            {
                "kind": "preview_video",
                "provider_url": preview.get("provider_url"),
                "local_path": preview.get("local_path"),
                "thumbnail_path": preview.get("thumbnail_path"),
                "file_size_bytes": preview.get("file_size_bytes"),
                "mime_type": "video/mp4",
            }
        )
    return json.dumps(payload, ensure_ascii=False)


@lru_cache(maxsize=16)
def _latest_version_id(model_id: str) -> str:
    """Return the current latest Replicate version ID for a model slug."""
    adapter = get_replicate_adapter()
    return adapter.get_latest_version_id(model_id)


def _run_prediction(
    model_id: str,
    input_params: dict,
    progress_callback: ProgressCallback | None = None,
    poll_interval: int = 10,
    use_versionless: bool = False,
) -> dict:
    """Create a Replicate prediction, poll, and return normalized output."""
    adapter = get_replicate_adapter()
    version_id = None if use_versionless else _latest_version_id(model_id)
    prediction = adapter.create_prediction(model_id, version_id, input_params)
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
        local = get_storage_service().download_output(mesh_url, "3d", prefix="model")
        assets_json = _serialize_3d_assets(mesh_url, local)
        record_generation(
            model_name=model.name,
            provider=model.provider,
            provider_model_id=model.provider_model_id or model.replicate_id,
            provider_job_id=result.get("prediction_id"),
            provider_job_url=result.get("prediction_url"),
            model_type="3d",
            prompt="",
            parameters=input_params,
            replicate_url=mesh_url,
            predict_time=result["predict_time"],
            total_time=result["total_time"],
            estimated_cost=cost,
            generation_mode="image_to_3d",
            input_image_path=_input_image_history_value(image),
            local_file_path=local.get("local_path"),
            thumbnail_path=local.get("thumbnail_path"),
            file_size_bytes=local.get("file_size_bytes"),
            output_assets_json=assets_json,
        )
        result["mesh_url"] = mesh_url
        result["local_file_path"] = local.get("local_path")
        result["thumbnail_path"] = local.get("thumbnail_path")
        result["file_size_bytes"] = local.get("file_size_bytes")
        result["estimated_cost"] = cost
        result["output_assets_json"] = assets_json
    return result


def generate_hunyuan_3d_3_1(
    prompt: str | None = None,
    image: Any | None = None,
    generate_type: str = "Normal",
    face_count: int = 500000,
    enable_pbr: bool = False,
    progress_callback: ProgressCallback | None = None,
) -> dict:
    """Hunyuan 3D 3.1 — Text-to-3D or Image-to-3D with textured mesh output.

    Requires exactly one of ``prompt`` or ``image``.
    Uses the versionless Replicate API (``model=`` not ``version=``).
    """
    model = HUNYUAN_3D_3_1
    input_params: dict[str, Any] = {}

    prompt_provided = prompt is not None and prompt.strip()
    image_provided = image is not None

    original_image = image

    if prompt_provided and image_provided:
        return {
            "success": False,
            "error": "Hunyuan 3D 3.1 accepts either text prompt or image, not both.",
            "prediction_id": "",
            "prediction_url": "",
        }
    if not prompt_provided and not image_provided:
        return {
            "success": False,
            "error": "Hunyuan 3D 3.1 needs either a text prompt or a subject image.",
            "prediction_id": "",
            "prediction_url": "",
        }

    if prompt_provided:
        input_params["prompt"] = prompt
    if image_provided:
        input_params["image"] = image_to_data_uri(
            image,
            allowed_extensions={".jpg", ".jpeg", ".png", ".webp"},
            max_size_bytes=6 * 1024 * 1024,
        )

    input_params["generate_type"] = generate_type
    input_params["face_count"] = face_count
    input_params["enable_pbr"] = enable_pbr

    validate_params(model, input_params)
    result = _run_prediction(
        model.replicate_id,
        input_params,
        progress_callback,
        use_versionless=True,
    )
    if result["success"]:
        output = result["output"]
        model_url = output_to_url(output)
        cost = calculate_cost(model.replicate_id, result["predict_time"])
        local = get_storage_service().download_output(model_url, "3d", prefix="model")
        generation_mode = "text_to_3d" if prompt else "image_to_3d"
        history_params = dict(input_params)
        if image_provided:
            history_params["image"] = uploaded_file_metadata(original_image)
        assets_json = _serialize_3d_assets(model_url, local)
        record_generation(
            model_name=model.name,
            provider=model.provider,
            provider_model_id=model.provider_model_id or model.replicate_id,
            provider_job_id=result.get("prediction_id"),
            provider_job_url=result.get("prediction_url"),
            model_type="3d",
            prompt=prompt or "",
            parameters=history_params,
            replicate_url=model_url,
            predict_time=result["predict_time"],
            total_time=result["total_time"],
            estimated_cost=cost,
            generation_mode=generation_mode,
            input_image_path=_input_image_history_value(original_image),
            local_file_path=local.get("local_path"),
            thumbnail_path=local.get("thumbnail_path"),
            file_size_bytes=local.get("file_size_bytes"),
            output_assets_json=assets_json,
        )
        result["model_url"] = model_url
        result["local_file_path"] = local.get("local_path")
        result["thumbnail_path"] = local.get("thumbnail_path")
        result["file_size_bytes"] = local.get("file_size_bytes")
        result["estimated_cost"] = cost
        result["output_assets_json"] = assets_json
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
        local = get_storage_service().download_output(model_url, "3d", prefix="model")
        preview_local = (
            get_storage_service().download_output(video_url, "video", prefix="preview")
            if video_url
            else {}
        )
        assets_json = _serialize_3d_assets(model_url, local, preview_local or None)
        record_generation(
            model_name=model.name,
            provider=model.provider,
            provider_model_id=model.provider_model_id or model.replicate_id,
            provider_job_id=result.get("prediction_id"),
            provider_job_url=result.get("prediction_url"),
            model_type="3d",
            prompt="",
            parameters=input_params,
            replicate_url=model_url,
            predict_time=result["predict_time"],
            total_time=result["total_time"],
            estimated_cost=cost,
            generation_mode="image_to_3d",
            input_image_path=_input_image_history_value(image),
            local_file_path=local.get("local_path"),
            thumbnail_path=preview_local.get("thumbnail_path")
            or local.get("thumbnail_path"),
            file_size_bytes=local.get("file_size_bytes"),
            output_assets_json=assets_json,
        )
        result["model_url"] = model_url
        result["video_url"] = video_url
        result["local_file_path"] = local.get("local_path")
        result["thumbnail_path"] = preview_local.get("thumbnail_path") or local.get(
            "thumbnail_path"
        )
        result["file_size_bytes"] = local.get("file_size_bytes")
        result["estimated_cost"] = cost
        result["output_assets_json"] = assets_json
    return result
