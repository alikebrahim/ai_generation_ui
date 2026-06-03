"""Cost tracking and generation history via SQLite.

Stores metadata about every generation: model, prompt, parameters,
cost estimate, and the Replicate output URL. No output files are
stored locally — only the URL reference.
"""

import json
import sqlite3

from .config import HISTORY_DB
from .utils import sanitize_parameters

# ── Schema ──────────────────────────────────────────────────────────

SCHEMA_SQL = """
CREATE TABLE IF NOT EXISTS generations (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name          TEXT    NOT NULL,
    model_type          TEXT    NOT NULL,
    timestamp           TEXT    NOT NULL DEFAULT (datetime('now')),
    prompt              TEXT,
    input_image_path    TEXT,
    parameters_json     TEXT,
    replicate_url       TEXT    NOT NULL,
    predict_time_s      REAL,
    total_time_s        REAL,
    estimated_cost_usd  REAL,
    output_duration_s   REAL,
    generation_mode     TEXT,
    status              TEXT    DEFAULT 'success'
);

CREATE INDEX IF NOT EXISTS idx_model_name ON generations(model_name);
CREATE INDEX IF NOT EXISTS idx_timestamp   ON generations(timestamp);
"""


# ── Public API ──────────────────────────────────────────────────────


def init_db() -> None:
    """Create database tables if they don't exist and apply tiny migrations."""
    conn = sqlite3.connect(str(HISTORY_DB))
    conn.executescript(SCHEMA_SQL)
    cursor = conn.execute("PRAGMA table_info(generations)")
    existing_columns = {row[1] for row in cursor.fetchall()}
    if "generation_mode" not in existing_columns:
        conn.execute("ALTER TABLE generations ADD COLUMN generation_mode TEXT")
    if "local_file_path" not in existing_columns:
        conn.execute("ALTER TABLE generations ADD COLUMN local_file_path TEXT")
    if "thumbnail_path" not in existing_columns:
        conn.execute("ALTER TABLE generations ADD COLUMN thumbnail_path TEXT")
    if "file_size_bytes" not in existing_columns:
        conn.execute("ALTER TABLE generations ADD COLUMN file_size_bytes INTEGER")
    conn.commit()
    conn.close()


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
) -> int:
    """Insert a generation record. Returns the new row id."""
    init_db()
    conn = sqlite3.connect(str(HISTORY_DB))
    cursor = conn.cursor()
    cursor.execute(
        """
        INSERT INTO generations (
            model_name, model_type, prompt, input_image_path,
            parameters_json, replicate_url, predict_time_s,
            total_time_s, estimated_cost_usd, output_duration_s,
            generation_mode, status, local_file_path, thumbnail_path,
            file_size_bytes
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            model_name,
            model_type,
            prompt,
            input_image_path,
            json.dumps(sanitize_parameters(parameters)),
            replicate_url,
            predict_time,
            total_time,
            estimated_cost,
            output_duration,
            generation_mode,
            status,
            local_file_path,
            thumbnail_path,
            file_size_bytes,
        ),
    )
    generation_id = cursor.lastrowid or 0
    conn.commit()
    conn.close()
    return generation_id


def get_all_generations(limit: int = 100) -> list[tuple]:
    """Return recent generations, newest first."""
    conn = sqlite3.connect(str(HISTORY_DB))
    cursor = conn.cursor()
    cursor.execute(
        """
        SELECT
            id, model_name, model_type, timestamp, prompt, input_image_path,
            parameters_json, replicate_url, predict_time_s, total_time_s,
            estimated_cost_usd, output_duration_s, generation_mode, status,
            local_file_path, thumbnail_path, file_size_bytes
        FROM generations
        ORDER BY timestamp DESC
        LIMIT ?
        """,
        (limit,),
    )
    rows = cursor.fetchall()
    conn.close()
    return rows


def get_stats_by_model() -> list[tuple]:
    """Return per-model stats: (model_name, count, total_cost, avg_time)."""
    conn = sqlite3.connect(str(HISTORY_DB))
    cursor = conn.cursor()
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
    return rows


def get_total_stats() -> tuple | None:
    """Return overall stats: (total_count, total_cost, avg_time)."""
    conn = sqlite3.connect(str(HISTORY_DB))
    cursor = conn.cursor()
    cursor.execute("""
        SELECT
            COUNT(*)                    AS total_count,
            SUM(estimated_cost_usd)     AS total_cost,
            AVG(predict_time_s)         AS avg_time
        FROM generations
        WHERE status = 'success'
    """)
    row = cursor.fetchone()
    conn.close()
    return row
