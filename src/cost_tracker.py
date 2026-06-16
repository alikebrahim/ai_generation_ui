"""Backward-compatible history API — delegates to HistoryService.

New code should import from ``src.history_service`` directly.
"""

from __future__ import annotations

from src.history_service import get_history_service, record_to_tuple

__all__ = [
    "get_all_generations",
    "get_stats_by_model",
    "get_total_stats",
    "init_db",
    "record_generation",
    "update_generation_thumbnail",
]


def init_db() -> None:
    """Create database tables if they don't exist and apply tiny migrations."""
    get_history_service().init_db()


def record_generation(
    *,
    model_name: str,
    model_type: str,
    prompt: str = "",
    parameters: dict | None = None,
    replicate_url: str,
    predict_time: float = 0.0,
    total_time: float = 0.0,
    estimated_cost: float = 0.0,
    output_duration: float | None = None,
    generation_mode: str | None = None,
    input_image_path: str | None = None,
    local_file_path: str | None = None,
    thumbnail_path: str | None = None,
    file_size_bytes: int | None = None,
    status: str = "success",
    provider: str = "replicate",
    provider_model_id: str | None = None,
    provider_job_id: str | None = None,
    provider_job_url: str | None = None,
    output_assets_json: str | None = None,
) -> int:
    """Insert a generation record. Returns the new row id."""
    return get_history_service().record_generation(
        model_name=model_name,
        model_type=model_type,
        provider=provider,
        prompt=prompt,
        parameters=parameters,
        predict_time_s=predict_time,
        total_time_s=total_time,
        estimated_cost_usd=estimated_cost,
        status=status,
        provider_model_id=provider_model_id,
        provider_job_id=provider_job_id,
        provider_job_url=provider_job_url,
        replicate_url=replicate_url,
        output_assets_json=output_assets_json,
        local_file_path=local_file_path,
        thumbnail_path=thumbnail_path,
        file_size_bytes=file_size_bytes,
        input_image_path=input_image_path,
        output_duration_s=output_duration,
        generation_mode=generation_mode,
    )


def get_all_generations(limit: int = 100) -> list[tuple]:
    """Return recent generations as legacy tuple rows, newest first."""
    records = get_history_service().get_all_generations(limit=limit)
    return [record_to_tuple(record) for record in records]


def update_generation_thumbnail(generation_id: int, thumbnail_path: str) -> None:
    """Persist a generated thumbnail path for an existing History row."""
    get_history_service().update_generation_thumbnail(generation_id, thumbnail_path)


def get_stats_by_model() -> list[tuple[str, int, float | None, float | None]]:
    """Return per-model stats: (model_name, count, total_cost, avg_time)."""
    return get_history_service().get_stats_by_model_rows()


def get_total_stats() -> tuple | None:
    """Return overall stats: (total_count, total_cost, avg_time)."""
    return get_history_service().get_total_stats()
