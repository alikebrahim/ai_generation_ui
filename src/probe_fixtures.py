"""Declarative non-paid validation probe kwargs per model."""

from __future__ import annotations

from typing import Any

from src.domain import ModelConfig

PROBE_IMAGE_FILE = {"name": "probe.png", "type": "image/png", "size": 100}
PROBE_OBJ_FILE = {"name": "probe.obj", "type": "model/obj", "size": 100}
PROBE_VIDEO_FILE = {"name": "probe.mp4", "type": "video/mp4", "size": 100}

# Placeholder tokens resolved at probe time.
_PROBE_IMAGE = "__probe_image__"
_PROBE_OBJ = "__probe_obj__"
_PROBE_VIDEO = "__probe_video__"

PROBE_KWARGS_BY_MODEL: dict[str, dict[str, Any]] = {
    "wan-2.7-t2v": {"prompt": "probe", "duration": 5, "resolution": "1080p"},
    "wan-2.5-i2v-fast": {
        "prompt": "probe",
        "image": _PROBE_IMAGE,
        "duration": 5,
    },
    "seedance-2.0": {"prompt": "probe", "duration": 5},
    "happyhorse-1.0": {
        "prompt": "probe",
        "duration": 5,
        "resolution": "720p",
        "_generation_mode": "text",
    },
    "gen-4.5": {"prompt": "probe", "duration": 5},
    "seedance-2.0-fast": {"prompt": "probe", "duration": 5},
    "kling-v3-omni": {"prompt": "probe", "duration": 5, "mode": "standard"},
    "dreamactor-m2.0": {"image": _PROBE_IMAGE, "video": _PROBE_VIDEO},
    "aleph-2": {"prompt": "probe edit", "video": _PROBE_VIDEO},
    "kling-v3-motion": {
        "image": _PROBE_IMAGE,
        "video": _PROBE_VIDEO,
        "mode": "std",
    },
    "kling-o1": {"prompt": "probe", "duration": 5},
    "hunyuan-3d-3.1": {"prompt": "probe chair"},
    "text2tex": {"prompt": "red fabric", "obj_file": _PROBE_OBJ},
    "adirik-texture": {"prompt": "wood grain", "shape_path": _PROBE_OBJ},
    "rodin": {"prompt": "a wooden chair"},
    "hunyuan3d-2mv": {"front_image": _PROBE_IMAGE},
    "music-2.5": {"lyrics": "verse one\nchorus"},
    "stable-audio-2.5": {"prompt": "ambient pad", "duration": 5},
    "lyria-2": {"prompt": "calm piano"},
    "realtime-tts-2": {"text": "Hello, this is a test."},
    "realtime-tts-1.5-max": {"text": "Hello, this is a test."},
    "speech-2.8-hd": {"text": "Hello, this is a test."},
    "speech-2.8-turbo": {"text": "Hello, this is a test."},
    "chatterbox": {"prompt": "Hello world"},
    "elevenlabs-v3": {"prompt": "Hello world"},
}


def _resolve_probe_value(value: Any) -> Any:
    if value == _PROBE_IMAGE:
        return PROBE_IMAGE_FILE
    if value == _PROBE_OBJ:
        return PROBE_OBJ_FILE
    if value == _PROBE_VIDEO:
        return PROBE_VIDEO_FILE
    return value


def get_probe_kwargs(model: ModelConfig) -> dict[str, Any]:
    """Return kwargs for a non-paid prepare_payload_for_model probe."""
    if model.probe_kwargs:
        raw = dict(model.probe_kwargs)
    elif model.name in PROBE_KWARGS_BY_MODEL:
        raw = dict(PROBE_KWARGS_BY_MODEL[model.name])
    elif model.requires_image:
        raw = {"image": _PROBE_IMAGE}
    elif model.requires_text or model.supports_text:
        raw = {"prompt": "probe"}
    else:
        raw = {"image": _PROBE_IMAGE}

    return {key: _resolve_probe_value(value) for key, value in raw.items()}
