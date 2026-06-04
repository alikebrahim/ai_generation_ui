"""Domain types and dataclasses for AI Generation Studio.

Shared internal structures for representing generation requests, results, and assets.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from src.output_asset import OutputAsset


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
