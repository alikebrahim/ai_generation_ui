"""Build Replicate input dicts for image generation models."""

from __future__ import annotations

from typing import Any

from src.utils import image_to_data_uri

_ARRAY_IMAGE_PARAMS = frozenset(
    {"image_input", "input_images", "style_reference_images"}
)
_URI_IMAGE_PARAMS = frozenset({"image", "mask"})


def _file_to_uri(value: Any) -> str:
    if isinstance(value, str):
        return value
    return image_to_data_uri(value)


def _files_to_uri_list(value: Any) -> list[str]:
    if value is None:
        return []
    items = value if isinstance(value, list) else [value]
    return [_file_to_uri(item) for item in items if item is not None]


def _pick(kwargs: dict[str, Any], *keys: str) -> dict[str, Any]:
    payload: dict[str, Any] = {}
    for key in keys:
        if key not in kwargs:
            continue
        value = kwargs[key]
        if key in _ARRAY_IMAGE_PARAMS:
            uris = _files_to_uri_list(value)
            if uris:
                payload[key] = uris
        elif key in _URI_IMAGE_PARAMS:
            if value is not None:
                payload[key] = _file_to_uri(value)
        elif value is not None:
            payload[key] = value
    return payload


def build_nano_banana_2_input(**kwargs: Any) -> dict[str, Any]:
    return _pick(
        kwargs,
        "prompt",
        "image_input",
        "aspect_ratio",
        "resolution",
        "google_search",
        "image_search",
        "output_format",
    )


def build_flux_2_max_input(**kwargs: Any) -> dict[str, Any]:
    return _pick(
        kwargs,
        "prompt",
        "input_images",
        "aspect_ratio",
        "resolution",
        "width",
        "height",
        "safety_tolerance",
        "seed",
        "output_format",
        "output_quality",
    )


def build_flux_2_pro_input(**kwargs: Any) -> dict[str, Any]:
    return build_flux_2_max_input(**kwargs)


def build_flux_2_flex_input(**kwargs: Any) -> dict[str, Any]:
    payload = build_flux_2_max_input(**kwargs)
    payload.update(
        _pick(
            kwargs,
            "prompt_upsampling",
            "steps",
            "guidance",
        )
    )
    return payload


def build_seedream_4_5_input(**kwargs: Any) -> dict[str, Any]:
    return _pick(
        kwargs,
        "prompt",
        "image_input",
        "size",
        "aspect_ratio",
        "width",
        "height",
        "sequential_image_generation",
        "max_images",
        "disable_safety_checker",
    )


def build_seedream_5_lite_input(**kwargs: Any) -> dict[str, Any]:
    return _pick(
        kwargs,
        "prompt",
        "image_input",
        "size",
        "aspect_ratio",
        "sequential_image_generation",
        "max_images",
        "output_format",
    )


def build_imagen_4_ultra_input(**kwargs: Any) -> dict[str, Any]:
    return _pick(
        kwargs,
        "prompt",
        "aspect_ratio",
        "image_size",
        "safety_filter_level",
        "output_format",
    )


def build_imagen_4_fast_input(**kwargs: Any) -> dict[str, Any]:
    return _pick(
        kwargs,
        "prompt",
        "aspect_ratio",
        "safety_filter_level",
        "output_format",
    )


def build_ideogram_v3_turbo_input(**kwargs: Any) -> dict[str, Any]:
    return _pick(
        kwargs,
        "prompt",
        "aspect_ratio",
        "resolution",
        "magic_prompt_option",
        "image",
        "mask",
        "style_type",
        "style_reference_images",
        "seed",
        "style_preset",
    )


def build_recraft_v4_input(**kwargs: Any) -> dict[str, Any]:
    return _pick(kwargs, "prompt", "aspect_ratio", "size")


def build_recraft_v4_svg_input(**kwargs: Any) -> dict[str, Any]:
    return build_recraft_v4_input(**kwargs)


def build_flux_schnell_input(**kwargs: Any) -> dict[str, Any]:
    return _pick(
        kwargs,
        "prompt",
        "aspect_ratio",
        "num_outputs",
        "num_inference_steps",
        "seed",
        "output_format",
        "output_quality",
        "disable_safety_checker",
        "go_fast",
        "megapixels",
    )


IMAGE_PAYLOAD_BUILDERS: dict[str, Any] = {
    "nano-banana-2": build_nano_banana_2_input,
    "flux-2-max": build_flux_2_max_input,
    "flux-2-pro": build_flux_2_pro_input,
    "seedream-4.5": build_seedream_4_5_input,
    "imagen-4-ultra": build_imagen_4_ultra_input,
    "seedream-5-lite": build_seedream_5_lite_input,
    "flux-2-flex": build_flux_2_flex_input,
    "ideogram-v3-turbo": build_ideogram_v3_turbo_input,
    "recraft-v4": build_recraft_v4_input,
    "recraft-v4-svg": build_recraft_v4_svg_input,
    "imagen-4-fast": build_imagen_4_fast_input,
    "flux-schnell": build_flux_schnell_input,
}
