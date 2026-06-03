"""Model configurations — identifiers, display names, parameter schemas.

Each ModelConfig captures:
- The Replicate model identifier (replicate_id)
- Which input modes are supported (text, image)
- Which parameters are Balanced (always visible) vs Advanced (in expander)
- Default values for all parameters
"""

from dataclasses import dataclass, field
from typing import Literal, TypedDict

ModelType = Literal["video", "3d"]


class ParamConstraint(TypedDict, total=False):
    """Validated per-parameter constraint from live Replicate schema.

    All values in this project's model configs were verified against the live
    Replicate OpenAPI schema (model.latest_version.openapi_schema) on 2026-06-03.
    """

    min: int | float
    max: int | float
    enum: list[str | int | float]
    ui_type: str  # "slider", "dropdown", "number", "checkbox"
    nullable: bool


@dataclass
class ModelConfig:
    """Configuration for a Replicate model."""

    name: str  # Short slug, e.g. "wan-2.7-t2v"
    display_name: str  # Human-readable, e.g. "Wan 2.7 T2V"
    model_type: ModelType
    replicate_id: str  # Replicate model identifier
    supports_text: bool
    supports_image: bool
    supports_audio: bool = False
    requires_text: bool = False
    requires_image: bool = False
    # Parameter groups
    balanced_params: list[str] = field(default_factory=list)
    advanced_params: list[str] = field(default_factory=list)
    # Default values per parameter
    defaults: dict = field(default_factory=dict)
    # Per-parameter schema constraints (live-validated against Replicate OpenAPI)
    param_constraints: dict[str, ParamConstraint] = field(default_factory=dict)
    # Groups of parameters that are mutually exclusive (at most one can be set)
    mutual_exclusion: list[tuple[str, ...]] = field(default_factory=list)
    # Groups where at least one parameter must be provided.
    required_one_of: list[tuple[str, ...]] = field(default_factory=list)


# ═══════════════════════════════════════════════
#  VIDEO MODELS
# ═══════════════════════════════════════════════

WAN_2_7_T2V = ModelConfig(
    name="wan-2.7-t2v",
    display_name="Wan 2.7 T2V",
    model_type="video",
    replicate_id="wan-video/wan-2.7-t2v",
    supports_text=True,
    supports_image=False,
    supports_audio=True,  # accepts audio uri for synchronization
    requires_text=True,
    balanced_params=[
        "prompt",
        "duration",
        "aspect_ratio",
        "seed",
        "resolution",
    ],
    advanced_params=[
        "negative_prompt",
        "enable_prompt_expansion",
    ],
    defaults={
        "duration": 5,
        "resolution": "1080p",
        "aspect_ratio": "16:9",
        "seed": -1,
        "enable_prompt_expansion": True,
        "negative_prompt": "",
    },
    param_constraints={
        "duration": {"min": 2, "max": 15, "ui_type": "slider"},
        "resolution": {"enum": ["720p", "1080p"], "ui_type": "dropdown"},
        "aspect_ratio": {
            "enum": ["16:9", "9:16", "1:1", "4:3", "3:4"],
            "ui_type": "dropdown",
        },
        "seed": {"nullable": True},
    },
)

WAN_2_5_I2V = ModelConfig(
    name="wan-2.5-i2v-fast",
    display_name="Wan 2.5 I2V Fast",
    model_type="video",
    replicate_id="wan-video/wan-2.5-i2v-fast",
    supports_text=True,
    supports_image=True,
    supports_audio=True,
    requires_text=True,
    requires_image=True,
    balanced_params=[
        "prompt",
        "image",
        "duration",
        "seed",
        "resolution",
    ],
    advanced_params=[
        "negative_prompt",
        "enable_prompt_expansion",
    ],
    defaults={
        "duration": 5,
        "resolution": "720p",
        "seed": -1,
        "enable_prompt_expansion": True,
        "negative_prompt": "",
    },
    param_constraints={
        "duration": {"enum": [5, 10], "ui_type": "dropdown"},
        "resolution": {"enum": ["720p", "1080p"], "ui_type": "dropdown"},
        "seed": {"nullable": True},
    },
)

SEEDANCE_2_0 = ModelConfig(
    name="seedance-2.0",
    display_name="Seedance 2.0",
    model_type="video",
    replicate_id="bytedance/seedance-2.0",
    supports_text=True,
    supports_image=True,
    supports_audio=True,
    requires_text=True,
    balanced_params=[
        "prompt",
        "image",
        "duration",
        "aspect_ratio",
        "seed",
        "resolution",
    ],
    advanced_params=[
        "generate_audio",
        "reference_images",
        "reference_videos",
        "reference_audios",
    ],
    defaults={
        "duration": 5,
        "resolution": "720p",
        "aspect_ratio": "16:9",
        "seed": -1,
        "generate_audio": True,
        "reference_images": [],
        "reference_videos": [],
        "reference_audios": [],
    },
    param_constraints={
        "duration": {"min": -1, "max": 15, "ui_type": "slider"},
        "resolution": {"enum": ["480p", "720p", "1080p"], "ui_type": "dropdown"},
        "aspect_ratio": {
            "enum": [
                "16:9", "4:3", "1:1", "3:4", "9:16",
                "21:9", "9:21", "adaptive",
            ],
            "ui_type": "dropdown",
        },
        "seed": {"nullable": True},
        "image": {"nullable": True},
    },
)


# ═══════════════════════════════════════════════
#  3D MODELS
# ═══════════════════════════════════════════════

HUNYUAN3D_2 = ModelConfig(
    name="hunyuan3d-2",
    display_name="Hunyuan3D 2.0",
    model_type="3d",
    replicate_id="tencent/hunyuan3d-2",
    supports_text=False,  # NOTE: Replicate schema shows image-only
    supports_image=True,
    requires_image=True,
    balanced_params=[
        "image",
        "seed",
    ],
    advanced_params=[
        "steps",
        "guidance_scale",
        "octree_resolution",
        "remove_background",
    ],
    defaults={
        "seed": 1234,
        "steps": 50,
        "guidance_scale": 5.5,
        "octree_resolution": 256,
        "remove_background": True,
    },
    param_constraints={
        "steps": {"min": 20, "max": 50, "ui_type": "number"},
        "guidance_scale": {"min": 1.0, "max": 20.0, "ui_type": "number"},
        "octree_resolution": {"enum": [256, 384, 512], "ui_type": "dropdown"},
    },
)

TRELLIS_2 = ModelConfig(
    name="trellis-2",
    display_name="TRELLIS 2",
    model_type="3d",
    replicate_id="fishwowater/trellis2",
    supports_text=False,
    supports_image=True,
    requires_image=True,
    balanced_params=[
        "image",
        "seed",
        "pipeline_type",
    ],
    advanced_params=[
        "generate_model",
        "generate_video",
        "texture_size",
        "decimation_target",
        "preprocess_image",
        "sparse_structure_steps",
        "shape_slat_steps",
        "tex_slat_steps",
        "shape_slat_guidance_strength",
        "tex_slat_guidance_strength",
    ],
    defaults={
        "seed": 42,
        "pipeline_type": "1024_cascade",
        "generate_model": True,
        "generate_video": True,
        "texture_size": 4096,
        "decimation_target": 1_000_000,
        "preprocess_image": True,
        "sparse_structure_steps": 12,
        "shape_slat_steps": 12,
        "tex_slat_steps": 12,
        "shape_slat_guidance_strength": 7.5,
        "tex_slat_guidance_strength": 1.0,
    },
    param_constraints={
        "pipeline_type": {
            "enum": ["512", "1024", "1024_cascade", "1536_cascade"],
            "ui_type": "dropdown",
        },
        "texture_size": {"min": 1024, "max": 8192, "ui_type": "number"},
        "decimation_target": {"min": 100000, "max": 2000000, "ui_type": "number"},
        "sparse_structure_steps": {"min": 1, "max": 50, "ui_type": "number"},
        "shape_slat_steps": {"min": 1, "max": 50, "ui_type": "number"},
        "tex_slat_steps": {"min": 1, "max": 50, "ui_type": "number"},
        "shape_slat_guidance_strength": {"min": 0.0, "max": 15.0, "ui_type": "number"},
        "tex_slat_guidance_strength": {"min": 0.0, "max": 15.0, "ui_type": "number"},
    },
)

HUNYUAN_3D_3_1 = ModelConfig(
    name="hunyuan-3d-3.1",
    display_name="Hunyuan 3D 3.1",
    model_type="3d",
    replicate_id="tencent/hunyuan-3d-3.1",
    supports_text=True,
    supports_image=True,
    requires_text=False,  # Either prompt or image is sufficient
    requires_image=False,  # Either prompt or image is sufficient
    balanced_params=[
        "prompt",
        "image",
        "generate_type",
        "face_count",
    ],
    advanced_params=[
        "enable_pbr",
    ],
    defaults={
        "generate_type": "Normal",
        "face_count": 500000,
        "enable_pbr": False,
    },
    param_constraints={
        "generate_type": {
            "enum": ["Normal", "Geometry"],
            "ui_type": "dropdown",
        },
        "face_count": {"min": 40000, "max": 1500000, "ui_type": "slider"},
        "prompt": {"nullable": True, "max": 1024},
        "image": {"nullable": True},
    },
    # Exactly one of prompt or image must be provided; both together is invalid.
    mutual_exclusion=[("prompt", "image")],
    required_one_of=[("prompt", "image")],
)


# ═══════════════════════════════════════════════
#  COLLECTIONS
# ═══════════════════════════════════════════════

VIDEO_MODELS: list[ModelConfig] = [WAN_2_7_T2V, WAN_2_5_I2V, SEEDANCE_2_0]
THREED_MODELS: list[ModelConfig] = [HUNYUAN3D_2, TRELLIS_2, HUNYUAN_3D_3_1]
ALL_MODELS: list[ModelConfig] = VIDEO_MODELS + THREED_MODELS

_MODEL_BY_NAME: dict[str, ModelConfig] = {m.name: m for m in ALL_MODELS}
_MODEL_BY_ID: dict[str, ModelConfig] = {m.replicate_id: m for m in ALL_MODELS}


def get_model_by_name(name: str) -> ModelConfig:
    """Look up a ModelConfig by its short name slug."""
    if name not in _MODEL_BY_NAME:
        raise ValueError(f"Unknown model: {name!r}. Known: {list(_MODEL_BY_NAME)}")
    return _MODEL_BY_NAME[name]


def get_model_by_replicate_id(replicate_id: str) -> ModelConfig:
    """Look up a ModelConfig by its Replicate model identifier."""
    if replicate_id not in _MODEL_BY_ID:
        raise ValueError(f"Unknown model ID: {replicate_id!r}")
    return _MODEL_BY_ID[replicate_id]


# ── Constraint query helpers (used by app.py validation & widget renderers) ──


def get_options_for_param(model: ModelConfig, param_name: str) -> list | None:
    """Return enum options if defined in model constraints, else None."""
    c = model.param_constraints.get(param_name, {})
    enum = c.get("enum")
    return list(enum) if enum else None


def get_range_for_param(
    model: ModelConfig, param_name: str,
) -> tuple[int | float | None, int | float | None]:
    """Return (min, max) for a numeric parameter, or (None, None)."""
    c = model.param_constraints.get(param_name, {})
    return (c.get("min"), c.get("max"))


def is_param_nullable(model: ModelConfig, param_name: str) -> bool:
    """Return True if the parameter accepts null/None."""
    c = model.param_constraints.get(param_name, {})
    return c.get("nullable", False)
