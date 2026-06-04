"""History service — provider-aware generation tracking with updated schema."""

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from typing import Any

from src.config import HISTORY_DB
from src.utils import sanitize_parameters

# Updated schema with provider metadata (v0.4.8+)
SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS generations (
    id                      INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name              TEXT    NOT NULL,
    model_type              TEXT    NOT NULL,
    timestamp               TEXT    NOT NULL DEFAULT (datetime('now')),
    prompt                  TEXT,
    input_image_path        TEXT,
    parameters_json         TEXT,
    replicate_url           TEXT,
    predict_time_s          REAL,
    total_time_s            REAL,
    estimated_cost_usd      REAL,
    output_duration_s       REAL,
    generation_mode         TEXT,
    status                  TEXT    DEFAULT 'success',
    local_file_path         TEXT,
    thumbnail_path          TEXT,
    file_size_bytes         INTEGER,
    -- Provider metadata (v0.4.8+)
    provider                TEXT    DEFAULT 'replicate',
    provider_model_id       TEXT,
    provider_job_id         TEXT,
    provider_job_url        TEXT,
    output_assets_json      TEXT
);
"""

INDEX_SQL = """
CREATE INDEX IF NOT EXISTS idx_model_name ON generations(model_name);
CREATE INDEX IF NOT EXISTS idx_timestamp   ON generations(timestamp);
CREATE INDEX IF NOT EXISTS idx_provider    ON generations(provider);
"""


@dataclass
class GenerationRecord:
    """Represents a single generation record from history."""

    id: int
    model_name: str
    model_type: str
    timestamp: str
    prompt: str | None
    provider: str
    provider_job_id: str | None
    provider_job_url: str | None
    estimated_cost_usd: float | None
    total_time_s: float | None
    status: str
    local_file_path: str | None
    replicate_url: str | None  # Preserved for backwards compat
    parameters_json: str | None = None
    input_image_path: str | None = None
    predict_time_s: float | None = None
    output_duration_s: float | None = None
    generation_mode: str | None = None
    thumbnail_path: str | None = None
    file_size_bytes: int | None = None
    provider_model_id: str | None = None
    output_assets_json: str | None = None

    @property
    def primary_url(self) -> str | None:
        """Return primary URL: local file path, provider URL, or None."""
        if self.local_file_path:
            return self.local_file_path
        return self.replicate_url or self.provider_job_url


class HistoryService:
    """Manages generation history with provider awareness."""

    def __init__(self, db_path: str = str(HISTORY_DB)):
        """Initialize history service."""
        self.db_path = db_path
        self.init_db()

    def init_db(self) -> None:
        """Create/migrate database schema."""
        conn = sqlite3.connect(self.db_path)
        # Important: create/upgrade columns before creating indexes that
        # reference newly-added columns. Existing v0.4.2 databases do not have
        # provider metadata yet.
        conn.executescript(SCHEMA_SQL)

        cursor = conn.execute("PRAGMA table_info(generations)")
        existing_cols = {row[1] for row in cursor.fetchall()}

        migrations = [
            ("generation_mode", "ADD COLUMN generation_mode TEXT"),
            ("local_file_path", "ADD COLUMN local_file_path TEXT"),
            ("thumbnail_path", "ADD COLUMN thumbnail_path TEXT"),
            ("file_size_bytes", "ADD COLUMN file_size_bytes INTEGER"),
            ("provider", "ADD COLUMN provider TEXT DEFAULT 'replicate'"),
            ("provider_model_id", "ADD COLUMN provider_model_id TEXT"),
            ("provider_job_id", "ADD COLUMN provider_job_id TEXT"),
            ("provider_job_url", "ADD COLUMN provider_job_url TEXT"),
            ("output_assets_json", "ADD COLUMN output_assets_json TEXT"),
        ]
        for column, alter_clause in migrations:
            if column not in existing_cols:
                conn.execute(f"ALTER TABLE generations {alter_clause}")

        conn.executescript(INDEX_SQL)
        conn.commit()
        conn.close()

    def record_generation(
        self,
        *,
        model_name: str,
        model_type: str,
        provider: str = "replicate",
        prompt: str = "",
        parameters: dict[str, Any] | None = None,
        predict_time_s: float = 0.0,
        total_time_s: float = 0.0,
        estimated_cost_usd: float = 0.0,
        status: str = "success",
        # Provider metadata
        provider_model_id: str | None = None,
        provider_job_id: str | None = None,
        provider_job_url: str | None = None,
        replicate_url: str | None = None,  # Backwards compat
        output_assets_json: str | None = None,
        # File paths
        local_file_path: str | None = None,
        thumbnail_path: str | None = None,
        file_size_bytes: int | None = None,
        input_image_path: str | None = None,
        output_duration_s: float | None = None,
        generation_mode: str | None = None,
    ) -> int:
        """Record a generation. Returns the new record ID."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute(
            """
            INSERT INTO generations (
                model_name, model_type, prompt, input_image_path,
                parameters_json, predict_time_s, total_time_s,
                estimated_cost_usd, output_duration_s, generation_mode, status,
                local_file_path, thumbnail_path, file_size_bytes,
                provider, provider_model_id, provider_job_id, provider_job_url,
                replicate_url, output_assets_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                model_name,
                model_type,
                prompt,
                input_image_path,
                json.dumps(sanitize_parameters(parameters)),
                predict_time_s,
                total_time_s,
                estimated_cost_usd,
                output_duration_s,
                generation_mode,
                status,
                local_file_path,
                thumbnail_path,
                file_size_bytes,
                provider,
                provider_model_id,
                provider_job_id,
                provider_job_url,
                replicate_url or provider_job_url or "",
                output_assets_json,
            ),
        )
        generation_id = cursor.lastrowid or 0
        conn.commit()
        conn.close()
        return generation_id

    def get_all_generations(
        self,
        limit: int = 100,
        provider: str | None = None,
    ) -> list[GenerationRecord]:
        """Get recent generations, optionally filtered by provider."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        if provider:
            cursor.execute(
                """
                SELECT * FROM generations
                WHERE provider = ?
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (provider, limit),
            )
        else:
            cursor.execute(
                """
                SELECT * FROM generations
                ORDER BY timestamp DESC
                LIMIT ?
                """,
                (limit,),
            )

        rows = cursor.fetchall()
        conn.close()
        return [GenerationRecord(**dict(row)) for row in rows]

    def get_stats_by_model(self, provider: str | None = None) -> dict[str, Any]:
        """Get per-model stats: count, total_cost, avg_time."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if provider:
            cursor.execute(
                """
                SELECT
                    model_name,
                    COUNT(*)                    AS count,
                    SUM(estimated_cost_usd)     AS total_cost,
                    AVG(predict_time_s)         AS avg_time
                FROM generations
                WHERE status = 'success' AND provider = ?
                GROUP BY model_name
                """,
                (provider,),
            )
        else:
            cursor.execute("""
                SELECT
                    model_name,
                    COUNT(*)                    AS count,
                    SUM(estimated_cost_usd)     AS total_cost,
                    AVG(predict_time_s)         AS avg_time
                FROM generations
                WHERE status = 'success'
                GROUP BY model_name
                """)

        rows = cursor.fetchall()
        conn.close()
        return {
            row[0]: {"count": row[1], "cost": row[2], "avg_time": row[3]}
            for row in rows
        }

    def get_total_cost(self, provider: str | None = None) -> float:
        """Return total estimated cost across all generations."""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        if provider:
            cursor.execute(
                """
                SELECT SUM(estimated_cost_usd) FROM generations
                WHERE status = 'success' AND provider = ?
                """,
                (provider,),
            )
        else:
            cursor.execute("""
                SELECT SUM(estimated_cost_usd) FROM generations
                WHERE status = 'success'
                """)

        result = cursor.fetchone()
        conn.close()
        return result[0] or 0.0


# Global singleton instance
_history_service = HistoryService()


def get_history_service() -> HistoryService:
    """Return the global history service instance."""
    return _history_service
