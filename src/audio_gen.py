"""Audio generation — thin wrapper over the shared generation pipeline."""

from __future__ import annotations

from src.generation_pipeline import generate_audio_model

__all__ = ["generate_audio_model"]
