"""Build Replicate prediction input dicts without creating paid predictions.

Generation handlers call these builders so dry-run previews match live payloads.
"""

from __future__ import annotations

from typing import Any

from src.audio_payload import AUDIO_PAYLOAD_BUILDERS
from src.image_payload import IMAGE_PAYLOAD_BUILDERS
from src.models_config import ModelConfig, get_model_by_name
from src.utils import image_to_data_uri, uploaded_file_metadata
from src.validation import ValidationError, validate_params

PayloadBuilder = Any  # Callable[..., dict[str, Any]]


def _optional_seed(seed: int | None) -> int | None:
    if seed is not None and seed >= 0:
        return seed
    return None


def _single_file_as_list(value: Any) -> list[Any] | None:
    if value is None:
        return None
    if isinstance(value, list):
        return value or None
    return [value]


def build_wan_2_7_t2v_input(
    prompt: str,
    duration: int = 5,
    resolution: str = "1080p",
    aspect_ratio: str = "16:9",
    seed: int | None = None,
    negative_prompt: str = "",
    enable_prompt_expansion: bool = True,
    audio: str | None = None,
    **_: Any,
) -> dict[str, Any]:
    """Build input dict for Wan 2.7 text-to-video."""
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
    return input_params


def build_wan_2_5_i2v_input(
    prompt: str,
    image: Any,
    duration: int = 5,
    resolution: str = "720p",
    seed: int | None = None,
    negative_prompt: str = "",
    enable_prompt_expansion: bool = True,
    audio: str | None = None,
    **_: Any,
) -> dict[str, Any]:
    """Build input dict for Wan 2.5 image-to-video."""
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
    return input_params


def build_seedance_2_0_input(
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
    **_: Any,
) -> dict[str, Any]:
    """Build input dict for Seedance 2.0."""
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
    return input_params


def build_hunyuan3d_2_input(
    image: Any,
    seed: int = 1234,
    steps: int = 50,
    guidance_scale: float = 5.5,
    octree_resolution: int = 256,
    remove_background: bool = True,
    **_: Any,
) -> dict[str, Any]:
    """Build input dict for Hunyuan3D 2.0."""
    return {
        "image": image,
        "seed": seed,
        "steps": steps,
        "guidance_scale": guidance_scale,
        "octree_resolution": octree_resolution,
        "remove_background": remove_background,
    }


def build_hunyuan_3d_3_1_input(
    prompt: str | None = None,
    image: Any | None = None,
    generate_type: str = "Normal",
    face_count: int = 500000,
    enable_pbr: bool = False,
    **_: Any,
) -> dict[str, Any]:
    """Build input dict for Hunyuan 3D 3.1 (text or image mode)."""
    input_params: dict[str, Any] = {}
    prompt_provided = prompt is not None and str(prompt).strip()
    image_provided = image is not None

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
    return input_params


def build_trellis_2_input(
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
    **_: Any,
) -> dict[str, Any]:
    """Build input dict for TRELLIS 2."""
    return {
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


def build_hunyuan3d_2mv_input(
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
    **_: Any,
) -> dict[str, Any]:
    """Build input dict for Hunyuan3D 2 multiview."""
    input_params: dict[str, Any] = {
        "front_image": front_image,
        "file_type": file_type,
        "target_face_num": target_face_num,
        "steps": steps,
        "guidance_scale": guidance_scale,
        "octree_resolution": octree_resolution,
        "num_chunks": num_chunks,
        "remove_background": remove_background,
        "seed": seed,
        "randomize_seed": randomize_seed,
    }
    if back_image is not None:
        input_params["back_image"] = back_image
    if left_image is not None:
        input_params["left_image"] = left_image
    if right_image is not None:
        input_params["right_image"] = right_image
    return input_params


def build_text2tex_input(
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
    **_: Any,
) -> dict[str, Any]:
    """Build input dict for Text2Tex mesh texturing."""
    input_params: dict[str, Any] = {
        "prompt": prompt,
        "obj_file": obj_file,
        "negative_prompt": negative_prompt,
        "ddim_steps": ddim_steps,
        "new_strength": new_strength,
        "update_strength": update_strength,
        "num_viewpoints": num_viewpoints,
        "viewpoint_mode": viewpoint_mode,
        "update_steps": update_steps,
        "update_mode": update_mode,
    }
    if seed is not None:
        input_params["seed"] = seed
    return input_params


def build_adirik_texture_input(
    shape_path: Any,
    prompt: str = "A next gen nascar",
    texture_resolution: int = 1024,
    guidance_scale: float = 10.0,
    shape_scale: float = 0.6,
    seed: int = 0,
    texture_interpolation_mode: str = "bilinear",
    **_: Any,
) -> dict[str, Any]:
    """Build input dict for Adirik texture generation."""
    return {
        "shape_path": shape_path,
        "prompt": prompt,
        "texture_resolution": texture_resolution,
        "guidance_scale": guidance_scale,
        "shape_scale": shape_scale,
        "seed": seed,
        "texture_interpolation_mode": texture_interpolation_mode,
    }


def build_rodin_input(
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
    **_: Any,
) -> dict[str, Any]:
    """Build input dict for Hyper3D Rodin Gen-2."""
    input_params: dict[str, Any] = {
        "prompt": prompt,
        "quality": quality,
        "geometry_file_format": geometry_file_format,
        "material": material,
        "mesh_mode": mesh_mode,
        "preview_render": preview_render,
        "use_original_alpha": use_original_alpha,
        "tapose": tapose,
        "tier": tier,
    }
    if seed is not None:
        input_params["seed"] = seed
    if images is not None:
        if isinstance(images, list):
            input_params["images"] = images
        else:
            input_params["images"] = [images]
    return input_params


def build_happyhorse_1_0_input(
    prompt: str = "",
    image: Any | None = None,
    duration: int = 5,
    resolution: str = "1080p",
    aspect_ratio: str = "16:9",
    seed: int | None = None,
    **_: Any,
) -> dict[str, Any]:
    """Build input dict for Happy Horse 1.0."""
    input_params: dict[str, Any] = {
        "duration": duration,
        "resolution": resolution,
    }
    if prompt:
        input_params["prompt"] = prompt
    if image:
        input_params["image"] = image
    elif aspect_ratio:
        input_params["aspect_ratio"] = aspect_ratio
    optional_seed = _optional_seed(seed)
    if optional_seed is not None:
        input_params["seed"] = optional_seed
    return input_params


def build_gen_4_5_input(
    prompt: str,
    duration: int = 5,
    aspect_ratio: str = "16:9",
    seed: int | None = None,
    image: Any | None = None,
    **_: Any,
) -> dict[str, Any]:
    """Build input dict for Runway Gen-4.5."""
    input_params: dict[str, Any] = {
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
    }
    if image:
        input_params["image"] = image
    optional_seed = _optional_seed(seed)
    if optional_seed is not None:
        input_params["seed"] = optional_seed
    return input_params


def build_seedance_2_0_fast_input(
    prompt: str,
    duration: int = 5,
    resolution: str = "720p",
    aspect_ratio: str = "16:9",
    seed: int | None = None,
    generate_audio: bool = True,
    image: Any | None = None,
    last_frame_image: Any | None = None,
    reference_images: Any | None = None,
    reference_videos: Any | None = None,
    reference_audios: Any | None = None,
    **_: Any,
) -> dict[str, Any]:
    """Build input dict for Seedance 2.0 Fast."""
    input_params: dict[str, Any] = {
        "prompt": prompt,
        "duration": duration,
        "resolution": resolution,
        "aspect_ratio": aspect_ratio,
        "generate_audio": generate_audio,
    }
    optional_seed = _optional_seed(seed)
    if optional_seed is not None:
        input_params["seed"] = optional_seed
    if image:
        input_params["image"] = image
    if last_frame_image:
        input_params["last_frame_image"] = last_frame_image
    refs = _single_file_as_list(reference_images)
    if refs:
        input_params["reference_images"] = refs
    vids = _single_file_as_list(reference_videos)
    if vids:
        input_params["reference_videos"] = vids
    auds = _single_file_as_list(reference_audios)
    if auds:
        input_params["reference_audios"] = auds
    return input_params


def build_kling_multimodal_input(
    prompt: str,
    mode: str = "pro",
    duration: int = 5,
    aspect_ratio: str = "16:9",
    generate_audio: bool = False,
    keep_original_sound: bool = True,
    video_reference_type: str = "feature",
    start_image: Any | None = None,
    end_image: Any | None = None,
    reference_images: Any | None = None,
    reference_video: Any | None = None,
    multi_prompt: str | None = None,
    **_: Any,
) -> dict[str, Any]:
    """Shared builder for Kling Omni-style multimodal video models."""
    input_params: dict[str, Any] = {
        "prompt": prompt,
        "mode": mode,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "keep_original_sound": keep_original_sound,
        "video_reference_type": video_reference_type,
    }
    if generate_audio:
        input_params["generate_audio"] = True
    if start_image:
        input_params["start_image"] = start_image
    if end_image:
        input_params["end_image"] = end_image
    if reference_video:
        input_params["reference_video"] = reference_video
    refs = _single_file_as_list(reference_images)
    if refs:
        input_params["reference_images"] = refs
    if multi_prompt:
        input_params["multi_prompt"] = multi_prompt
    return input_params


def build_kling_v3_omni_input(**kwargs: Any) -> dict[str, Any]:
    """Build input dict for Kling 3 Omni Video."""
    return build_kling_multimodal_input(**kwargs)


def build_kling_o1_input(**kwargs: Any) -> dict[str, Any]:
    """Build input dict for Kling O1."""
    return build_kling_multimodal_input(**kwargs)


def build_dreamactor_m2_0_input(
    image: Any,
    video: Any,
    cut_first_second: bool = True,
    **_: Any,
) -> dict[str, Any]:
    """Build input dict for Dreamactor M2.0."""
    return {
        "image": image,
        "video": video,
        "cut_first_second": cut_first_second,
    }


def build_aleph_2_input(
    prompt: str,
    video: Any,
    seed: int | None = None,
    **_: Any,
) -> dict[str, Any]:
    """Build input dict for Runway Aleph 2.0 (no keyframes in v0.6.10 UI)."""
    input_params: dict[str, Any] = {
        "prompt": prompt,
        "video": video,
    }
    optional_seed = _optional_seed(seed)
    if optional_seed is not None:
        input_params["seed"] = optional_seed
    return input_params


def build_kling_v3_motion_input(
    image: Any,
    video: Any,
    mode: str = "pro",
    character_orientation: str = "image",
    keep_original_sound: bool = True,
    prompt: str = "",
    **_: Any,
) -> dict[str, Any]:
    """Build input dict for Kling 3 Motion Control."""
    input_params: dict[str, Any] = {
        "image": image,
        "video": video,
        "mode": mode,
        "character_orientation": character_orientation,
        "keep_original_sound": keep_original_sound,
    }
    if prompt:
        input_params["prompt"] = prompt
    return input_params


PAYLOAD_BUILDERS: dict[str, PayloadBuilder] = {
    "wan-2.7-t2v": build_wan_2_7_t2v_input,
    "wan-2.5-i2v-fast": build_wan_2_5_i2v_input,
    "seedance-2.0": build_seedance_2_0_input,
    "happyhorse-1.0": build_happyhorse_1_0_input,
    "gen-4.5": build_gen_4_5_input,
    "seedance-2.0-fast": build_seedance_2_0_fast_input,
    "kling-v3-omni": build_kling_v3_omni_input,
    "dreamactor-m2.0": build_dreamactor_m2_0_input,
    "aleph-2": build_aleph_2_input,
    "kling-v3-motion": build_kling_v3_motion_input,
    "kling-o1": build_kling_o1_input,
    "hunyuan3d-2": build_hunyuan3d_2_input,
    "hunyuan3d-2mv": build_hunyuan3d_2mv_input,
    "hunyuan-3d-3.1": build_hunyuan_3d_3_1_input,
    "trellis-2": build_trellis_2_input,
    "text2tex": build_text2tex_input,
    "adirik-texture": build_adirik_texture_input,
    "rodin": build_rodin_input,
    **AUDIO_PAYLOAD_BUILDERS,
    **IMAGE_PAYLOAD_BUILDERS,
}


def build_replicate_input(model_name: str, **kwargs: Any) -> dict[str, Any]:
    """Return the Replicate ``input`` dict for a model slug."""
    if model_name not in PAYLOAD_BUILDERS:
        raise ValueError(f"No payload builder for model: {model_name!r}")
    clean = {
        key: value
        for key, value in kwargs.items()
        if key not in {"progress_callback", "_uploaded_image"}
    }
    uploaded = kwargs.get("_uploaded_image")
    if uploaded is not None and "image" not in clean:
        clean["image"] = uploaded
    uploaded_images = kwargs.get("_uploaded_images")
    if uploaded_images is not None and "images" not in clean:
        clean["images"] = uploaded_images
    for key, value in kwargs.items():
        if key.startswith("_uploaded_") and key not in {
            "_uploaded_image",
            "_uploaded_images",
        }:
            param = key.removeprefix("_uploaded_")
            if param not in clean:
                clean[param] = value
    return PAYLOAD_BUILDERS[model_name](**clean)


def prepare_payload_for_model(
    model: ModelConfig,
    **kwargs: Any,
) -> dict[str, Any]:
    """Validate kwargs and build the Replicate input payload for a model."""
    clean = {
        key: value
        for key, value in kwargs.items()
        if key not in {"progress_callback", "_uploaded_image"}
    }
    uploaded = kwargs.get("_uploaded_image")
    if uploaded is not None:
        clean["image"] = uploaded

    if model.name == "rodin" and kwargs.get("_generation_mode") == "reference":
        if kwargs.get("_uploaded_images") is None:
            raise ValidationError(
                "Rodin reference mode needs a reference image upload."
            )

    if model.name == "hunyuan-3d-3.1":
        prompt_provided = bool(str(clean.get("prompt") or "").strip())
        image_provided = clean.get("image") is not None
        if prompt_provided and image_provided:
            raise ValidationError(
                "Hunyuan 3D 3.1 accepts either a text prompt or a subject image, "
                "not both."
            )
        if not prompt_provided and not image_provided:
            raise ValidationError(
                "Hunyuan 3D 3.1 needs either a text prompt or a subject image."
            )

    if model.name == "happyhorse-1.0":
        mode = kwargs.get("_generation_mode", "text")
        if mode == "text" and not str(clean.get("prompt") or "").strip():
            raise ValidationError("Happy Horse needs a text prompt for text-to-video.")
        if mode == "image" and clean.get("image") is None:
            raise ValidationError(
                "Happy Horse needs a start frame image for image-to-video."
            )

    payload = build_replicate_input(model.name, **kwargs)
    validate_payload_for_model(model, payload)
    return payload


def validate_payload_for_model(model: ModelConfig, payload: dict[str, Any]) -> None:
    """Run cross-field and schema validation on a built Replicate input dict."""
    _validate_video_payload_rules(model, payload)
    validate_params(model, payload)


def _has_media_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, list):
        return len(value) > 0
    if isinstance(value, str):
        return bool(value.strip())
    return True


def _validate_video_payload_rules(
    model: ModelConfig, payload: dict[str, Any]
) -> None:
    """Extra cross-field rules for v0.6.10 video models."""
    if model.name == "kling-v3-omni":
        if payload.get("generate_audio") and payload.get("reference_video"):
            raise ValidationError(
                "Kling Omni cannot use native audio together with a reference video."
            )
        if payload.get("mode") == "4k" and payload.get("reference_video"):
            raise ValidationError(
                "Kling Omni 4K mode does not support reference video."
            )
    if payload.get("end_image") and not (
        payload.get("start_image") or payload.get("image")
    ):
        raise ValidationError("End frame requires a start frame image first.")
    if payload.get("last_frame_image") and not payload.get("image"):
        raise ValidationError(
            "End frame requires a start frame image first."
        )
    if model.name in ("seedance-2.0", "seedance-2.0-fast"):
        if _has_media_value(payload.get("reference_audios")):
            has_anchor = any(
                _has_media_value(payload.get(key))
                for key in (
                    "reference_images",
                    "reference_videos",
                    "image",
                    "last_frame_image",
                )
            )
            if not has_anchor:
                raise ValidationError(
                    "Reference audio requires at least one reference image, "
                    "reference video, or start frame image."
                )


def generation_mode_for_payload(model: ModelConfig, payload: dict[str, Any]) -> str:
    """Infer generation_mode from built payload and model type."""
    if model.model_type == "audio":
        tags = getattr(model, "workflow_tags", []) or []
        if "music" in tags:
            return "text_to_music"
        return "text_to_speech"
    if model.model_type == "image":
        has_refs = any(
            _has_media_value(payload.get(key))
            for key in (
                "image_input",
                "input_images",
                "image",
                "style_reference_images",
            )
        )
        if "vector_svg" in (model.workflow_tags or []):
            return "text_to_vector"
        if has_refs or payload.get("mask"):
            return "image_edit"
        return "text_to_image"
    if model.model_type == "video":
        if model.workflow_archetype == "motion_transfer":
            return "motion_transfer"
        if model.workflow_archetype == "video_edit":
            return "video_edit"
        if payload.get("reference_video") and payload.get(
            "video_reference_type"
        ) == "base":
            return "video_edit"
        if payload.get("reference_videos") or payload.get("reference_video"):
            return "multimodal_video"
        if payload.get("reference_images") or payload.get("reference_audios"):
            return "multimodal_video"
        if payload.get("image") is not None or payload.get("start_image") is not None:
            return "image_to_video"
        return "text_to_video"
    if model.name == "hunyuan-3d-3.1":
        if payload.get("prompt"):
            return "text_to_3d"
        return "image_to_3d"
    if model.name == "text2tex":
        return "mesh_texturing"
    if model.name == "adirik-texture":
        return "mesh_texturing"
    if model.name == "rodin":
        if payload.get("images"):
            return "image_to_3d"
        return "text_to_3d"
    if model.name == "hunyuan3d-2mv":
        return "multiview_to_3d"
    return "image_to_3d"


def summarize_payload_value(value: Any) -> Any:
    """Replace file-like values with safe metadata for JSON display."""
    if value is None:
        return None
    if isinstance(value, str):
        if value.startswith("data:"):
            return {
                "_type": "data_uri",
                "mime_type": value.split(";")[0].replace("data:", ""),
                "length_chars": len(value),
            }
        if len(value) > 200:
            return {
                "_type": "string",
                "length_chars": len(value),
                "preview": value[:80],
            }
        return value
    meta = uploaded_file_metadata(value)
    if meta:
        return {"_type": "uploaded_file", **meta}
    if isinstance(value, list):
        return [summarize_payload_value(item) for item in value]
    return value


def get_model_by_name_for_payload(name: str) -> ModelConfig:
    """Thin wrapper to keep imports localized."""
    return get_model_by_name(name)
