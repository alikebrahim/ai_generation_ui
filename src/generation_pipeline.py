"""Shared generation pipeline: predict → cost → store → history."""

from __future__ import annotations

import json
from collections.abc import Callable
from functools import lru_cache
from typing import Any

from src.history_service import get_history_service
from src.models_config import ModelConfig, get_model_by_name
from src.pricing import calculate_cost
from src.providers import get_replicate_adapter
from src.replicate_payload import (
    generation_mode_for_payload,
    prepare_payload_for_model,
)
from src.storage_service import get_storage_service
from src.utils import output_to_url, sanitize_parameters, uploaded_file_metadata

ProgressCallback = Callable[[str, object], None]

_POLL_INTERVALS = {"video": 5, "audio": 5, "3d": 10, "image": 5}
_HISTORY_SKIP_KEYS = frozenset(
    {
        "reference_images",
        "reference_videos",
        "reference_audios",
        "keyframe_images",
        "keyframe_positions",
    }
)


@lru_cache(maxsize=16)
def _latest_version_id(model_id: str) -> str:
    """Return the current latest Replicate version ID for a model slug."""
    return get_replicate_adapter().get_latest_version_id(model_id)


def run_replicate_prediction(
    model: ModelConfig,
    input_params: dict[str, Any],
    progress_callback: ProgressCallback | None = None,
    *,
    poll_interval: int | None = None,
) -> dict[str, Any]:
    """Create a Replicate prediction, poll it, and return a normalized result."""
    adapter = get_replicate_adapter()
    model_id = model.provider_model_id or model.replicate_id
    version_id: str | None = None
    if model.provider_endpoint == "versioned":
        version_id = _latest_version_id(model_id)

    interval = poll_interval or _POLL_INTERVALS.get(model.model_type, 5)
    prediction = adapter.create_prediction(model_id, version_id, input_params)
    prediction = adapter.wait_for_prediction(
        prediction,
        poll_interval=interval,
        progress_callback=progress_callback,
    )
    if prediction.status != "succeeded":
        return adapter.prediction_result_dict(prediction)

    output = prediction.output
    if model.model_type == "3d":
        if isinstance(output, list):
            pass
        elif isinstance(output, str) or hasattr(output, "url"):
            output = {"mesh": output}
        return adapter.prediction_result_dict(
            prediction,
            success_output={"output": output},
        )

    if isinstance(output, list):
        urls = [output_to_url(item) for item in output]
        urls = [url for url in urls if url]
        primary = urls[0] if urls else ""
        return adapter.prediction_result_dict(
            prediction,
            success_output={"url": primary, "urls": urls},
        )

    return adapter.prediction_result_dict(
        prediction,
        success_output={"url": output_to_url(output)},
    )


def _input_image_history_value(image: Any) -> str | None:
    """Return a safe history value for image input without serializing bytes."""
    if isinstance(image, str):
        return image if image.startswith(("http", "data:")) else None
    meta = uploaded_file_metadata(image)
    return meta.get("filename") if meta else None


def _history_parameters(input_params: dict[str, Any]) -> dict[str, Any]:
    """Replace file-like values with safe metadata for SQLite history."""
    history: dict[str, Any] = {}
    for key, value in input_params.items():
        if key in _HISTORY_SKIP_KEYS:
            continue
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


def _serialize_video_assets(primary_url: str, local: dict[str, Any]) -> str:
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


def _serialize_3d_assets(
    primary_url: str,
    local: dict[str, Any],
    preview: dict[str, Any] | None = None,
) -> str:
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


def _record_generation(
    *,
    model: ModelConfig,
    prompt: str,
    parameters: dict[str, Any],
    replicate_url: str,
    result: dict[str, Any],
    cost: float,
    generation_mode: str,
    local: dict[str, Any],
    assets_json: str,
    input_image_path: str | None = None,
    output_duration: float | None = None,
) -> None:
    get_history_service().record_generation(
        model_name=model.name,
        model_type=model.model_type,
        provider=model.provider,
        provider_model_id=model.provider_model_id or model.replicate_id,
        provider_job_id=result.get("prediction_id"),
        provider_job_url=result.get("prediction_url"),
        prompt=prompt,
        parameters=parameters,
        replicate_url=replicate_url,
        predict_time_s=result.get("predict_time", 0),
        total_time_s=result.get("total_time", 0),
        estimated_cost_usd=cost,
        output_duration_s=output_duration,
        generation_mode=generation_mode,
        input_image_path=input_image_path,
        local_file_path=local.get("local_path"),
        thumbnail_path=local.get("thumbnail_path"),
        file_size_bytes=local.get("file_size_bytes"),
        output_assets_json=assets_json,
    )


def _enrich_success(
    result: dict[str, Any],
    *,
    local: dict[str, Any],
    cost: float,
    assets_json: str,
    **extra: Any,
) -> dict[str, Any]:
    result["local_file_path"] = local.get("local_path")
    result["thumbnail_path"] = local.get("thumbnail_path")
    result["file_size_bytes"] = local.get("file_size_bytes")
    result["estimated_cost"] = cost
    result["output_assets_json"] = assets_json
    result.update(extra)
    return result


def _billing_duration(input_params: dict[str, Any]) -> float:
    duration = input_params.get("duration")
    if isinstance(duration, (int, float)) and duration > 0:
        return float(duration)
    return 5.0


def _billing_text_length(payload: dict[str, Any]) -> int:
    total = 0
    for key in ("lyrics", "text", "prompt"):
        val = payload.get(key)
        if isinstance(val, str):
            total += len(val)
    return total


def _primary_text_for_history(payload: dict[str, Any]) -> str:
    for key in ("lyrics", "text", "prompt"):
        val = payload.get(key)
        if isinstance(val, str) and val.strip():
            return val.strip()
    return ""


def finalize_video_result(
    model: ModelConfig,
    input_params: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    """Download, record history, and enrich a successful video result."""
    if not result.get("success"):
        return result

    bill_duration = _billing_duration(input_params)
    cost = calculate_cost(
        model.replicate_id,
        result.get("predict_time", 0),
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
    _record_generation(
        model=model,
        prompt=prompt,
        parameters=history_params,
        replicate_url=result["url"],
        result=result,
        cost=cost,
        generation_mode=generation_mode_for_payload(model, input_params),
        local=local,
        assets_json=assets_json,
        input_image_path=_input_image_history_value(
            input_params.get("image") or input_params.get("start_image")
        ),
        output_duration=bill_duration,
    )
    return _enrich_success(result, local=local, cost=cost, assets_json=assets_json)


def finalize_audio_result(
    model: ModelConfig,
    input_params: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    """Download, record history, and enrich a successful audio result."""
    if not result.get("success"):
        return result

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
    _record_generation(
        model=model,
        prompt=prompt,
        parameters=history_params,
        replicate_url=result["url"],
        result=result,
        cost=cost,
        generation_mode=generation_mode_for_payload(model, input_params),
        local=local,
        assets_json=assets_json,
    )
    return _enrich_success(result, local=local, cost=cost, assets_json=assets_json)


def _finalize_simple_3d(
    *,
    model: ModelConfig,
    input_params: dict[str, Any],
    result: dict[str, Any],
    generation_mode: str,
    prompt: str = "",
    input_image_path: str | None = None,
) -> dict[str, Any]:
    model_url = _primary_output_url(result.get("output"))
    cost = calculate_cost(model.replicate_id, result.get("predict_time", 0))
    local = get_storage_service().download_output(model_url, "3d", prefix="model")
    assets_json = _serialize_3d_assets(model_url, local)
    _record_generation(
        model=model,
        prompt=prompt,
        parameters=_history_parameters(input_params),
        replicate_url=model_url,
        result=result,
        cost=cost,
        generation_mode=generation_mode,
        local=local,
        assets_json=assets_json,
        input_image_path=input_image_path,
    )
    return _enrich_success(
        result,
        local=local,
        cost=cost,
        assets_json=assets_json,
        model_url=model_url,
    )


def finalize_threed_result(
    model: ModelConfig,
    input_params: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    """Download, record history, and enrich a successful 3D result."""
    if not result.get("success"):
        return result

    if model.name == "hunyuan3d-2":
        mesh_url = output_to_url(result["output"].get("mesh", result["output"]))
        cost = calculate_cost(model.replicate_id, result.get("predict_time", 0))
        local = get_storage_service().download_output(mesh_url, "3d", prefix="model")
        assets_json = _serialize_3d_assets(mesh_url, local)
        _record_generation(
            model=model,
            prompt="",
            parameters=input_params,
            replicate_url=mesh_url,
            result=result,
            cost=cost,
            generation_mode="image_to_3d",
            local=local,
            assets_json=assets_json,
            input_image_path=_input_image_history_value(input_params.get("image")),
        )
        return _enrich_success(
            result,
            local=local,
            cost=cost,
            assets_json=assets_json,
            mesh_url=mesh_url,
        )

    if model.name == "hunyuan-3d-3.1":
        output = result["output"]
        model_url = output_to_url(output)
        cost = calculate_cost(model.replicate_id, result.get("predict_time", 0))
        local = get_storage_service().download_output(model_url, "3d", prefix="model")
        prompt_provided = bool(str(input_params.get("prompt") or "").strip())
        generation_mode = "text_to_3d" if prompt_provided else "image_to_3d"
        history_params = dict(input_params)
        if input_params.get("image") is not None:
            history_params["image"] = uploaded_file_metadata(input_params.get("image"))
        assets_json = _serialize_3d_assets(model_url, local)
        _record_generation(
            model=model,
            prompt=str(input_params.get("prompt") or ""),
            parameters=history_params,
            replicate_url=model_url,
            result=result,
            cost=cost,
            generation_mode=generation_mode,
            local=local,
            assets_json=assets_json,
            input_image_path=_input_image_history_value(input_params.get("image")),
        )
        return _enrich_success(
            result,
            local=local,
            cost=cost,
            assets_json=assets_json,
            model_url=model_url,
        )

    if model.name == "trellis-2":
        output = result["output"]
        model_url = output_to_url(output.get("model_file", output))
        video_url = output_to_url(output.get("video", ""))
        cost = calculate_cost(model.replicate_id, result.get("predict_time", 0))
        local = get_storage_service().download_output(model_url, "3d", prefix="model")
        preview_local = (
            get_storage_service().download_output(video_url, "video", prefix="preview")
            if video_url
            else {}
        )
        preview_payload = (
            {
                "provider_url": video_url,
                "local_path": preview_local.get("local_path"),
                "thumbnail_path": preview_local.get("thumbnail_path"),
                "file_size_bytes": preview_local.get("file_size_bytes"),
            }
            if video_url
            else None
        )
        assets_json = _serialize_3d_assets(model_url, local, preview_payload)
        _record_generation(
            model=model,
            prompt="",
            parameters=input_params,
            replicate_url=model_url,
            result=result,
            cost=cost,
            generation_mode="image_to_3d",
            local=local,
            assets_json=assets_json,
            input_image_path=_input_image_history_value(input_params.get("image")),
        )
        thumbnail = preview_local.get("thumbnail_path") or local.get("thumbnail_path")
        result["video_url"] = video_url
        result["thumbnail_path"] = thumbnail
        return _enrich_success(
            result,
            local=local,
            cost=cost,
            assets_json=assets_json,
            model_url=model_url,
            thumbnail_path=thumbnail,
        )

    if model.name == "adirik-texture":
        output = result.get("output")
        urls = (
            [output_to_url(item) for item in output if output_to_url(item)]
            if isinstance(output, list)
            else [_primary_output_url(output)]
        )
        urls = [url for url in urls if url]
        model_url = urls[0] if urls else ""
        cost = calculate_cost(model.replicate_id, result.get("predict_time", 0))
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
        prompt = str(input_params.get("prompt") or "")
        _record_generation(
            model=model,
            prompt=prompt,
            parameters=_history_parameters(input_params),
            replicate_url=model_url,
            result=result,
            cost=cost,
            generation_mode="mesh_texturing",
            local=local,
            assets_json=assets_json,
        )
        return _enrich_success(
            result,
            local=local,
            cost=cost,
            assets_json=assets_json,
            model_url=model_url,
        )

    if model.name == "hunyuan3d-2mv":
        return _finalize_simple_3d(
            model=model,
            input_params=input_params,
            result=result,
            generation_mode="multiview_to_3d",
            input_image_path=_input_image_history_value(input_params.get("front_image")),
        )

    if model.name == "text2tex":
        return _finalize_simple_3d(
            model=model,
            input_params=input_params,
            result=result,
            generation_mode="mesh_texturing",
            prompt=str(input_params.get("prompt") or ""),
        )

    if model.name == "rodin":
        mode = "image_to_3d" if input_params.get("images") else "text_to_3d"
        image_ref = None
        if input_params.get("images"):
            imgs = input_params["images"]
            image_ref = _input_image_history_value(
                imgs[0] if isinstance(imgs, list) else imgs
            )
        return _finalize_simple_3d(
            model=model,
            input_params=input_params,
            result=result,
            generation_mode=mode,
            prompt=str(input_params.get("prompt") or ""),
            input_image_path=image_ref,
        )

    return _finalize_simple_3d(
        model=model,
        input_params=input_params,
        result=result,
        generation_mode="image_to_3d",
        prompt=str(input_params.get("prompt") or ""),
        input_image_path=_input_image_history_value(input_params.get("image")),
    )


def _serialize_image_assets(
    primary_url: str,
    local: dict[str, Any],
    *,
    urls: list[str] | None = None,
    all_locals: list[dict[str, Any]] | None = None,
) -> str:
    if all_locals:
        payload = []
        for idx, asset_local in enumerate(all_locals):
            url = urls[idx] if urls and idx < len(urls) else primary_url
            payload.append(
                {
                    "kind": "image",
                    "provider_url": url,
                    "local_path": asset_local.get("local_path"),
                    "file_size_bytes": asset_local.get("file_size_bytes"),
                    "mime_type": asset_local.get("mime_type") or "image/png",
                }
            )
        return json.dumps(payload, ensure_ascii=False)
    payload = [
        {
            "kind": "image",
            "provider_url": primary_url,
            "local_path": local.get("local_path"),
            "file_size_bytes": local.get("file_size_bytes"),
            "mime_type": local.get("mime_type") or "image/png",
        }
    ]
    return json.dumps(payload, ensure_ascii=False)


def finalize_image_result(
    model: ModelConfig,
    input_params: dict[str, Any],
    result: dict[str, Any],
) -> dict[str, Any]:
    """Download, record history, and enrich a successful image result."""
    if not result.get("success"):
        return result

    urls: list[str] = list(result.get("urls") or [])
    primary_url = str(result.get("url") or "")
    if primary_url and primary_url not in urls:
        urls.insert(0, primary_url)
    if not urls and primary_url:
        urls = [primary_url]
    if not urls:
        return result

    bill_count = max(len(urls), 1)
    cost = calculate_cost(
        model.replicate_id,
        result.get("predict_time", 0),
        output_count=bill_count,
    )
    locals_list: list[dict[str, Any]] = []
    for idx, url in enumerate(urls):
        prefix = "image" if idx == 0 else f"image_{idx}"
        locals_list.append(
            get_storage_service().download_output(url, "image", prefix=prefix)
        )
    local = locals_list[0]
    assets_json = _serialize_image_assets(
        urls[0],
        local,
        urls=urls if len(urls) > 1 else None,
        all_locals=locals_list if len(locals_list) > 1 else None,
    )
    prompt = str(input_params.get("prompt") or "")
    ref_image = (
        input_params.get("image")
        or (input_params.get("image_input") or [None])[0]
        or (input_params.get("input_images") or [None])[0]
    )
    _record_generation(
        model=model,
        prompt=prompt,
        parameters=_history_parameters(input_params),
        replicate_url=urls[0],
        result=result,
        cost=cost,
        generation_mode=generation_mode_for_payload(model, input_params),
        local=local,
        assets_json=assets_json,
        input_image_path=_input_image_history_value(ref_image),
    )
    extra: dict[str, Any] = {}
    if len(urls) > 1:
        extra["urls"] = urls
        extra["all_local_paths"] = [
            item.get("local_path") for item in locals_list if item.get("local_path")
        ]
    return _enrich_success(
        result,
        local=local,
        cost=cost,
        assets_json=assets_json,
        **extra,
    )


def generate_video_model(
    model_name: str,
    progress_callback: ProgressCallback | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Run any configured video model through the shared prediction pipeline."""
    model = get_model_by_name(model_name)
    input_params = prepare_payload_for_model(model, **kwargs)
    result = run_replicate_prediction(model, input_params, progress_callback)
    return finalize_video_result(model, input_params, result)


def generate_audio_model(
    model_name: str,
    progress_callback: ProgressCallback | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Run any configured audio model through the shared prediction pipeline."""
    model = get_model_by_name(model_name)
    input_params = prepare_payload_for_model(model, **kwargs)
    result = run_replicate_prediction(model, input_params, progress_callback)
    return finalize_audio_result(model, input_params, result)


def generate_threed_model(
    model_name: str,
    progress_callback: ProgressCallback | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Run any configured 3D model through the shared prediction pipeline."""
    model = get_model_by_name(model_name)
    input_params = prepare_payload_for_model(model, **kwargs)
    result = run_replicate_prediction(model, input_params, progress_callback)
    return finalize_threed_result(model, input_params, result)


def generate_image_model(
    model_name: str,
    progress_callback: ProgressCallback | None = None,
    **kwargs: Any,
) -> dict[str, Any]:
    """Run any configured image model through the shared prediction pipeline."""
    model = get_model_by_name(model_name)
    input_params = prepare_payload_for_model(model, **kwargs)
    result = run_replicate_prediction(model, input_params, progress_callback)
    return finalize_image_result(model, input_params, result)
