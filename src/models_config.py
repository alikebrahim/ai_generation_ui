"""Model configurations — identifiers, display names, parameter schemas.

Each ModelConfig captures:
- The Replicate model identifier (replicate_id)
- Which input modes are supported (text, image)
- Which parameters are Balanced (always visible) vs Advanced (in expander)
- Default values for all parameters
"""

from dataclasses import dataclass, field
from typing import Literal

ModelType = Literal["video", "3d"]


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
)


# ═══════════════════════════════════════════════
#  COLLECTIONS
# ═══════════════════════════════════════════════

VIDEO_MODELS: list[ModelConfig] = [WAN_2_7_T2V, WAN_2_5_I2V, SEEDANCE_2_0]
THREED_MODELS: list[ModelConfig] = [HUNYUAN3D_2, TRELLIS_2]
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
