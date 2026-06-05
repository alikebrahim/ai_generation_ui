"""Domain types and dataclasses for AI Generation Studio.

Shared internal structures for representing generation requests, results, and assets.

Also hosts the core ModelConfig dataclass (and supporting type aliases +
ParamConstraint) so that src/audio_models_config.py can import it without
creating a circular dependency with src/models_config.py (which aggregates
ALL_MODELS by importing the audio lists at the bottom of its module body).
models_config.py re-exports ModelConfig etc. for full backward compatibility
of all existing `from src.models_config import ...` sites.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Literal, TypedDict

from src.output_asset import OutputAsset

# ── Model catalogue types (moved here from models_config.py for cycle breaking) ──

ModelType = Literal["video", "3d", "audio"]
ProviderName = Literal["replicate", "fal"]
ProviderEndpointMode = Literal["versionless", "versioned"]
WorkflowArchetype = Literal[
    "text_or_image_video",
    "multimodal_video",
    "motion_transfer",
    "video_edit",
]


class ParamConstraint(TypedDict, total=False):
    """Validated per-parameter constraint from live Replicate schema.

    All values in this project's model configs were verified against the live
    Replicate OpenAPI schema (model.latest_version.openapi_schema); see
    metadata_verified_date on each ModelConfig.
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
    # Provider metadata (v0.4.5+)
    provider: ProviderName = "replicate"
    # Can differ from replicate_id for future fal.ai integration
    provider_model_id: str | None = None
    provider_endpoint: ProviderEndpointMode = "versionless"
    # Human-readable media role labels and mode selectors
    media_roles: dict[str, str] = field(default_factory=dict)
    generation_modes: list[tuple[str, str]] = field(default_factory=list)
    default_generation_mode: str | None = None
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
    # v0.6 metadata audit (source: Replicate model page + OpenAPI, date in field)
    metadata_verified_date: str = ""
    replicate_page_url: str = ""
    pricing_notes: str = ""
    output_notes: str = ""
    multi_output: bool = False
    # Param name → allowed file extensions for st.file_uploader (v0.6.5+)
    file_input_params: dict[str, list[str]] = field(default_factory=dict)
    required_file_params: list[str] = field(default_factory=list)
    # v0.6.10 video workflow UI
    workflow_archetype: WorkflowArchetype | None = None
    workflow_tags: list[str] = field(default_factory=list)
    # v0.6.6+ creative param exposure & UX
    param_help: dict[str, str] = field(default_factory=dict)
    high_impact_params: list[str] = field(default_factory=list)
    advanced_param_groups: list[tuple[str, list[str]]] = field(default_factory=list)
    # Per-model presets for quick creative starting points (e.g. "Fast preview").
    # Value = partial {param: value} applied to session keys for the widgets.
    presets: dict[str, dict[str, Any]] = field(default_factory=dict)


# ── Other domain types ──


@dataclass
class CostEstimate:
    """Cost estimation for a generation."""

    amount_usd: float
    is_known: bool = True
    source: str = "pricing_table"

    def __str__(self) -> str:
        if not self.is_known:
            return "Unknown"
        return f"${self.amount_usd:.4f}"


@dataclass
class GenerationResult:
    """Result of a single generation attempt."""

    success: bool
    model_name: str
    # generation_mode: "text_to_video", "image_to_video", "image_to_3d", "text_to_3d"
    generation_mode: str
    predict_time: float  # seconds
    estimated_cost: float = 0.0
    error: str | None = None
    prediction_id: str | None = None
    prediction_url: str | None = None

    # Legacy dict keys for backward compatibility during transition
    # Remove these after v0.4.9 when all code uses the dataclass
    url: str | None = None  # Primary output URL
    model_url: str | None = None
    mesh_url: str | None = None
    video_url: str | None = None
    local_file_path: str | None = None
    assets: list[OutputAsset] | None = None

    # For dict-like access during transition
    def __getitem__(self, key: str) -> Any:
        if key == "success":
            return self.success
        if key == "predict_time":
            return self.predict_time
        if key == "estimated_cost":
            return self.estimated_cost
        if key == "error":
            return self.error
        if key == "prediction_id":
            return self.prediction_id
        if key == "prediction_url":
            return self.prediction_url
        if key == "url":
            return self.url
        if key == "model_url":
            return self.model_url
        if key == "mesh_url":
            return self.mesh_url
        if key == "video_url":
            return self.video_url
        if key == "local_file_path":
            return self.local_file_path
        raise KeyError(key)

    def __contains__(self, key: str) -> bool:
        return key in {
            "success",
            "predict_time",
            "estimated_cost",
            "error",
            "prediction_id",
            "prediction_url",
            "url",
            "model_url",
            "mesh_url",
            "video_url",
            "local_file_path",
        }

    def get(self, key: str, default: Any = None) -> Any:
        """Dict-like get for backward compatibility."""
        try:
            return self[key]
        except KeyError:
            return default
