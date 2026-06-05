"""3D generation functions — Replicate 3D and texture workflows.

Pattern identical to video_gen.py:
  build input → run prediction → extract output → cost → record → return.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from functools import lru_cache
from typing import Any

from src.cost_tracker import record_generation
from src.models_config import (
    ADIRIK_TEXTURE,
    HUNYUAN3D_2,
    HUNYUAN3D_2MV,
    HUNYUAN_3D_3_1,
    RODIN,
    TEXT2TEX,
    TRELLIS_2,
)
from src.pricing import calculate_cost
from src.providers import get_replicate_adapter
from src.replicate_payload import (
    build_adirik_texture_input,
    build_hunyuan3d_2_input,
    build_hunyuan3d_2mv_input,
    build_hunyuan_3d_3_1_input,
    build_rodin_input,
    build_text2tex_input,
    build_trellis_2_input,
)
from src.storage_service import get_storage_service
from src.utils import output_to_url, uploaded_file_metadata
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
    prediction = adapter.wait_for_prediction(
        prediction,
        poll_interval=poll_interval,
        progress_callback=progress_callback,
    )
    if prediction.status != "succeeded":
        return adapter.prediction_result_dict(prediction)

    output = prediction.output
    if isinstance(output, list):
        pass
    elif isinstance(output, str) or hasattr(output, "url"):
        output = {"mesh": output}

    return adapter.prediction_result_dict(
        prediction,
        success_output={"output": output},
    )


def _primary_output_url(output: Any) -> str:
    """Extract the primary downloadable URL from a Replicate 3D output."""
    if isinstance(output, list):
        for item in output:
            url = output_to_url(item)
            if url:
                return url
        return ""
    if isinstance(output, dict):
        return output_to_url(output.get("model_file", output.get("mesh", output)))
    return output_to_url(output)


def _history_parameters(input_params: dict[str, Any]) -> dict[str, Any]:
    """Replace file-like values with safe metadata for SQLite history."""
    history: dict[str, Any] = {}
    for key, value in input_params.items():
        meta = uploaded_file_metadata(value)
        if meta:
            history[key] = meta
        elif isinstance(value, list):
            history[key] = [
                uploaded_file_metadata(item) or item for item in value
            ]
        else:
            history[key] = value
    return history


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
    input_params = build_hunyuan3d_2_input(
        image=image,
        seed=seed,
        steps=steps,
        guidance_scale=guidance_scale,
        octree_resolution=octree_resolution,
        remove_background=remove_background,
    )
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

    input_params = build_hunyuan_3d_3_1_input(
        prompt=prompt,
        image=image,
        generate_type=generate_type,
        face_count=face_count,
        enable_pbr=enable_pbr,
    )
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
        generation_mode = "text_to_3d" if prompt_provided else "image_to_3d"
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
    input_params = build_trellis_2_input(
        image=image,
        seed=seed,
        pipeline_type=pipeline_type,
        generate_model=generate_model,
        generate_video=generate_video,
        texture_size=texture_size,
        decimation_target=decimation_target,
        preprocess_image=preprocess_image,
        sparse_structure_steps=sparse_structure_steps,
        shape_slat_steps=shape_slat_steps,
        tex_slat_steps=tex_slat_steps,
        shape_slat_guidance_strength=shape_slat_guidance_strength,
        tex_slat_guidance_strength=tex_slat_guidance_strength,
    )
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


def _complete_simple_3d(
    *,
    model: Any,
    input_params: dict[str, Any],
    result: dict,
    generation_mode: str,
    prompt: str = "",
    input_image_path: str | None = None,
) -> dict:
    """Download, record history, and enrich a successful URI-based 3D result."""
    model_url = _primary_output_url(result.get("output"))
    cost = calculate_cost(model.replicate_id, result["predict_time"])
    local = get_storage_service().download_output(model_url, "3d", prefix="model")
    assets_json = _serialize_3d_assets(model_url, local)
    record_generation(
        model_name=model.name,
        provider=model.provider,
        provider_model_id=model.provider_model_id or model.replicate_id,
        provider_job_id=result.get("prediction_id"),
        provider_job_url=result.get("prediction_url"),
        model_type="3d",
        prompt=prompt,
        parameters=_history_parameters(input_params),
        replicate_url=model_url,
        predict_time=result["predict_time"],
        total_time=result["total_time"],
        estimated_cost=cost,
        generation_mode=generation_mode,
        input_image_path=input_image_path,
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


def generate_hunyuan3d_2mv(
    front_image: Any,
    file_type: str = "glb",
    target_face_num: int = 10000,
    back_image: Any | None = None,
    left_image: Any | None = None,
    right_image: Any | None = None,
    steps: int = 30,
    guidance_scale: float = 5.0,
    octree_resolution: int = 256,
    num_chunks: int = 200000,
    remove_background: bool = True,
    seed: int = 1234,
    randomize_seed: bool = True,
    progress_callback: ProgressCallback | None = None,
) -> dict:
    """Hunyuan3D 2 multiview — front image required, optional side/back views."""
    model = HUNYUAN3D_2MV
    input_params = build_hunyuan3d_2mv_input(
        front_image=front_image,
        file_type=file_type,
        target_face_num=target_face_num,
        back_image=back_image,
        left_image=left_image,
        right_image=right_image,
        steps=steps,
        guidance_scale=guidance_scale,
        octree_resolution=octree_resolution,
        num_chunks=num_chunks,
        remove_background=remove_background,
        seed=seed,
        randomize_seed=randomize_seed,
    )
    validate_params(model, input_params)
    result = _run_prediction(model.replicate_id, input_params, progress_callback)
    if result["success"]:
        return _complete_simple_3d(
            model=model,
            input_params=input_params,
            result=result,
            generation_mode="multiview_to_3d",
            input_image_path=_input_image_history_value(front_image),
        )
    return result


def generate_text2tex(
    prompt: str,
    obj_file: Any,
    negative_prompt: str = "",
    ddim_steps: int = 50,
    new_strength: float = 1.0,
    update_strength: float = 0.3,
    num_viewpoints: int = 36,
    viewpoint_mode: str = "predefined",
    update_steps: int = 20,
    update_mode: str = "heuristic",
    seed: int | None = None,
    progress_callback: ProgressCallback | None = None,
) -> dict:
    """Text2Tex — texture an existing .obj mesh from a text description."""
    model = TEXT2TEX
    input_params = build_text2tex_input(
        prompt=prompt,
        obj_file=obj_file,
        negative_prompt=negative_prompt,
        ddim_steps=ddim_steps,
        new_strength=new_strength,
        update_strength=update_strength,
        num_viewpoints=num_viewpoints,
        viewpoint_mode=viewpoint_mode,
        update_steps=update_steps,
        update_mode=update_mode,
        seed=seed,
    )
    validate_params(model, input_params)
    result = _run_prediction(model.replicate_id, input_params, progress_callback)
    if result["success"]:
        return _complete_simple_3d(
            model=model,
            input_params=input_params,
            result=result,
            generation_mode="mesh_texturing",
            prompt=prompt,
        )
    return result


def generate_adirik_texture(
    shape_path: Any,
    prompt: str = "A next gen nascar",
    texture_resolution: int = 1024,
    guidance_scale: float = 10.0,
    shape_scale: float = 0.6,
    seed: int = 0,
    texture_interpolation_mode: str = "bilinear",
    progress_callback: ProgressCallback | None = None,
) -> dict:
    """Adirik texture — apply a text prompt to an uploaded mesh."""
    model = ADIRIK_TEXTURE
    input_params = build_adirik_texture_input(
        shape_path=shape_path,
        prompt=prompt,
        texture_resolution=texture_resolution,
        guidance_scale=guidance_scale,
        shape_scale=shape_scale,
        seed=seed,
        texture_interpolation_mode=texture_interpolation_mode,
    )
    validate_params(model, input_params)
    result = _run_prediction(model.replicate_id, input_params, progress_callback)
    if result["success"]:
        output = result.get("output")
        urls = (
            [output_to_url(item) for item in output if output_to_url(item)]
            if isinstance(output, list)
            else [_primary_output_url(output)]
        )
        urls = [u for u in urls if u]
        model_url = urls[0] if urls else ""
        cost = calculate_cost(model.replicate_id, result["predict_time"])
        local = get_storage_service().download_output(model_url, "3d", prefix="model")
        assets: list[dict[str, Any]] = []
        for idx, url in enumerate(urls):
            asset_local = (
                local
                if idx == 0
                else get_storage_service().download_output(
                    url, "3d", prefix=f"model_{idx}"
                )
            )
            assets.append(
                {
                    "kind": "model",
                    "provider_url": url,
                    "local_path": asset_local.get("local_path"),
                    "thumbnail_path": asset_local.get("thumbnail_path"),
                    "file_size_bytes": asset_local.get("file_size_bytes"),
                    "mime_type": "model/gltf-binary",
                }
            )
        assets_json = json.dumps(assets, ensure_ascii=False)
        record_generation(
            model_name=model.name,
            provider=model.provider,
            provider_model_id=model.provider_model_id or model.replicate_id,
            provider_job_id=result.get("prediction_id"),
            provider_job_url=result.get("prediction_url"),
            model_type="3d",
            prompt=prompt,
            parameters=_history_parameters(input_params),
            replicate_url=model_url,
            predict_time=result["predict_time"],
            total_time=result["total_time"],
            estimated_cost=cost,
            generation_mode="mesh_texturing",
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


def generate_rodin(
    prompt: str,
    quality: str = "medium",
    geometry_file_format: str = "glb",
    material: str = "PBR",
    mesh_mode: str = "Quad",
    images: Any | None = None,
    preview_render: bool = False,
    seed: int | None = None,
    use_original_alpha: bool = False,
    tapose: bool = False,
    tier: str = "Gen-2",
    progress_callback: ProgressCallback | None = None,
) -> dict:
    """Hyper3D Rodin Gen-2 — text-to-3D with optional reference image."""
    model = RODIN
    input_params = build_rodin_input(
        prompt=prompt,
        quality=quality,
        geometry_file_format=geometry_file_format,
        material=material,
        mesh_mode=mesh_mode,
        images=images,
        preview_render=preview_render,
        seed=seed,
        use_original_alpha=use_original_alpha,
        tapose=tapose,
        tier=tier,
    )
    validate_params(model, input_params)
    result = _run_prediction(model.replicate_id, input_params, progress_callback)
    if result["success"]:
        mode = "image_to_3d" if input_params.get("images") else "text_to_3d"
        image_ref = None
        if input_params.get("images"):
            imgs = input_params["images"]
            image_ref = _input_image_history_value(
                imgs[0] if isinstance(imgs, list) else imgs
            )
        return _complete_simple_3d(
            model=model,
            input_params=input_params,
            result=result,
            generation_mode=mode,
            prompt=prompt,
            input_image_path=image_ref,
        )
    return result
