"""Model configurations — identifiers, display names, parameter schemas.

Aggregates video, 3D, and audio catalogues. Each ModelConfig captures:
- The Replicate model identifier (replicate_id)
- Which input modes are supported (text, image)
- Which parameters are Balanced (always visible) vs Advanced (in expander)
- Default values for all parameters
"""

from __future__ import annotations

from src.audio_models_config import AUDIO_MODELS
from src.domain import (  # noqa: F401
    ModelConfig,
    ModelType,
    ParamConstraint,
    ProviderEndpointMode,
    ProviderName,
    WorkflowArchetype,
)
from src.image_models_config import IMAGE_MODELS
from src.threed_models_config import (  # noqa: F401
    ADIRIK_TEXTURE,
    HUNYUAN3D_2,
    HUNYUAN3D_2MV,
    HUNYUAN_3D_3_1,
    RODIN,
    TEXT2TEX,
    THREED_MODELS,
    TRELLIS_2,
)
from src.video_models_config import (  # noqa: F401
    ALEPH_2,
    DREAMACTOR_M2_0,
    GEN_4_5,
    HAPPYHORSE_1_0,
    KLING_O1,
    KLING_V3_MOTION,
    KLING_V3_OMNI,
    SEEDANCE_2_0,
    SEEDANCE_2_0_FAST,
    VIDEO_MODELS,
    WAN_2_5_I2V,
    WAN_2_7_T2V,
)

ALL_MODELS: list[ModelConfig] = (
    VIDEO_MODELS + THREED_MODELS + AUDIO_MODELS + IMAGE_MODELS
)

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


def get_options_for_param(model: ModelConfig, param_name: str) -> list | None:
    """Return enum options if defined in model constraints, else None."""
    c = model.param_constraints.get(param_name, {})
    enum = c.get("enum")
    return list(enum) if enum else None


def get_range_for_param(
    model: ModelConfig,
    param_name: str,
) -> tuple[int | float | None, int | float | None]:
    """Return (min, max) for a numeric parameter, or (None, None)."""
    c = model.param_constraints.get(param_name, {})
    return (c.get("min"), c.get("max"))


def is_param_nullable(model: ModelConfig, param_name: str) -> bool:
    """Return True if the parameter accepts null/None."""
    c = model.param_constraints.get(param_name, {})
    return c.get("nullable", False)
