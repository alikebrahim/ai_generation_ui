# ITER_1_IMPLEMENTATION.md

**Date**: 2026-06-03
**Status**: Complete
**Project**: ai-generation-ui — Streamlit interface for Replicate-powered video & 3D generation

---

## Overview

A single-page Streamlit app with three tabs (Video, 3D, History) that generates AI media via the Replicate API. No local file storage — outputs preview inline from Replicate URLs and the user downloads to their browser when they want to keep something.

---

## Directory Structure

```
ai_generation_ui/
├── app.py                        ← Streamlit entry point
├── src/
│   ├── __init__.py               ← package marker
│   ├── config.py                 ← .env loading, token validation, paths, constants
│   ├── pricing.py                ← static hardware pricing table + cost calculator
│   ├── models_config.py          ← 5 ModelConfig dataclasses (real Replicate schemas)
│   ├── cost_tracker.py           ← SQLite: schema, insert, query, aggregate stats
│   ├── utils.py                  ← format_cost(), format_duration(), format_timestamp()
│   ├── video_gen.py              ← generate_wan_2_7_t2v(), generate_wan_2_5_i2v(), generate_seedance_2_0()
│   └── threed_gen.py             ← generate_hunyuan3d_2(), generate_trellis_2()
├── .gitignore
├── .env.example                  ← template (user copies to .env and adds token)
├── pyproject.toml                ← uv-compatible, deps: streamlit, replicate, pandas, etc.
├── data/                         ← SQLite database lands here (gitignored)
├── assets/                       ← reserved for future static files
├── ROADMAP.md                    ← future iteration plans (not implemented yet)
├── AGENTS.md                     ← agent context document
├── DECISIONS.md                  ← resolved design decisions
├── IMPLEMENTATION_PLAN.md        ← original 20-step plan (pre-implementation)
└── README.md                     ← project readme
```

---

## Architecture

```
┌─────────────────────────────────────────────────────┐
│                     app.py                          │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Video   │  │   3D     │  │     History      │  │
│  │  Tab     │  │  Tab     │  │     Tab          │  │
│  │          │  │          │  │  ┌──────────────┐ │  │
│  │ Model    │  │ Model    │  │  │ Summary      │ │  │
│  │ Selector │  │ Selector │  │  │ Cards        │ │  │
│  │   ↓      │  │   ↓      │  │  ├──────────────┤ │  │
│  │ Params   │  │ Params   │  │  │ Per-Model    │ │  │
│  │ Form     │  │ Form     │  │  │ Breakdown    │ │  │
│  │   ↓      │  │   ↓      │  │  ├──────────────┤ │  │
│  │ Generate │  │ Generate │  │  │ Recent       │ │  │
│  │   ↓      │  │   ↓      │  │  │ Gens Table   │ │  │
│  │ Preview  │  │ Preview  │  │  └──────────────┘ │  │
│  │ + DL     │  │ + DL     │  │                    │  │
│  └──────────┘  └──────────┘  └────────────────────┘  │
│                         │                            │
│            ┌────────────┼────────────┐               │
│            ↓            ↓            ↓               │
│     video_gen.py  threed_gen.py  cost_tracker.py     │
│            │            │            │               │
│            └────────────┼────────────┘               │
│                         ↓                            │
│                 Replicate API                        │
│          (wan-video, bytedance, tencent,             │
│           fishwowater models)                        │
│                         │                            │
│                         ↓                            │
│                   SQLite DB                          │
│               (data/history.db)                      │
└─────────────────────────────────────────────────────┘
```

---

## Implemented Models (5)

### Video Models

| # | Name | Replicate ID | Input Modes | Key Params |
|---|------|-------------|-------------|------------|
| 1 | Wan 2.7 T2V | `wan-video/wan-2.7-t2v` | Text, Audio | duration, resolution, aspect_ratio, negative_prompt, enable_prompt_expansion |
| 2 | Wan 2.5 I2V Fast | `wan-video/wan-2.5-i2v-fast` | Image, Text, Audio | same as above + image input |
| 3 | Seedance 2.0 | `bytedance/seedance-2.0` | Text, Image, Audio, Multi-ref | generate_audio, reference_images (up to 9), reference_videos (up to 3), reference_audios (up to 3) |

### 3D Models

| # | Name | Replicate ID | Input Modes | Key Params |
|---|------|-------------|-------------|------------|
| 4 | Hunyuan3D 2.0 | `tencent/hunyuan3d-2` | Image only | steps, guidance_scale, octree_resolution, remove_background |
| 5 | TRELLIS 2 | `fishwowater/trellis2` | Image only | pipeline_type, generate_model, generate_video, texture_size, decimation_target, multi-stage guidance |

> **Note**: Hunyuan3D 2.0 on Replicate does NOT accept text prompts (image-to-3D only). This differs from the original assumption in DECISIONS.md.

---

## Module Reference

### `src/config.py`

- Loads `.env` via `python-dotenv` (silent if file missing)
- Exports `REPLICATE_API_TOKEN` (may be None)
- `check_token()` — raises `RuntimeError` with setup instructions if token missing
- Paths: `PROJECT_ROOT`, `DATA_DIR`, `ASSETS_DIR`, `HISTORY_DB`
- Constants: `POLL_INTERVAL_VIDEO=5`, `POLL_INTERVAL_3D=10`, `MAX_RETRIES=3`
- Auto-creates `data/` and `assets/` directories on import

### `src/models_config.py`

- `ModelConfig` dataclass with fields: `name`, `display_name`, `model_type` (`"video"` | `"3d"`), `replicate_id`, `supports_text`, `supports_image`, `supports_audio`, `balanced_params`, `advanced_params`, `defaults`
- 5 instances: `WAN_2_7_T2V`, `WAN_2_5_I2V`, `SEEDANCE_2_0`, `HUNYUAN3D_2`, `TRELLIS_2`
- Collections: `VIDEO_MODELS`, `THREED_MODELS`, `ALL_MODELS`
- Lookup functions: `get_model_by_name(name)`, `get_model_by_replicate_id(id)`
- All parameter names match the actual Replicate API schema for each model

### `src/pricing.py`

- `HARDWARE_PRICING` — USD per compute-second for T4, L40S, A40, A100-40GB, A100-80GB, H100
- `MODEL_HARDWARE` — maps each Replicate model ID to its hardware
- `PER_SECOND_OUTPUT_PRICING` — for video models that charge by output duration (Wan: $0.10/s, Seedance: $0.15/s)
- `calculate_cost(model_id, predict_time, output_duration=None)` — returns estimated USD
- Prefers output-duration pricing when available, falls back to compute-time × hardware-rate

### `src/cost_tracker.py`

- SQLite database at `data/history.db` (auto-created on first `init_db()` call)
- Schema: `generations` table with columns: id, model_name, model_type, timestamp, prompt, input_image_path, parameters_json, replicate_url, predict_time_s, total_time_s, estimated_cost_usd, output_duration_s, status
- Indexes on `model_name` and `timestamp`
- `init_db()` — CREATE TABLE IF NOT EXISTS (idempotent)
- `record_generation(**kwargs)` — inserts a row, returns new row id
- `get_all_generations(limit=100)` — newest-first list of rows
- `get_stats_by_model()` — per-model (name, count, total_cost, avg_time)
- `get_total_stats()` — overall (total_count, total_cost, avg_time)

### `src/video_gen.py`

Common pattern for all three functions:

1. Build `input_params` dict from user kwargs
2. `replicate.predictions.create(model=..., input=input_params)`
3. Poll via `replicate.predictions.get(prediction.id)` until completion
4. Check `prediction.status`, normalize `prediction.output` into display/storage URLs
5. Calculate cost via `calculate_cost()`
6. `record_generation()` to SQLite
7. Return `{"success": True/False, "url": ..., "predict_time": ..., "estimated_cost": ...}`

Functions:
- `generate_wan_2_7_t2v(prompt, duration, resolution, aspect_ratio, seed, negative_prompt, enable_prompt_expansion, audio)`
- `generate_wan_2_5_i2v(prompt, image, duration, resolution, seed, negative_prompt, enable_prompt_expansion, audio)`
- `generate_seedance_2_0(prompt, duration, resolution, aspect_ratio, seed, generate_audio, image, last_frame_image, reference_images, reference_videos, reference_audios)`

### `src/threed_gen.py`

Same pattern as video, but 3D models return structured output (dict with keys like `mesh`, `model_file`, `video`):

- `generate_hunyuan3d_2(image, seed, steps, guidance_scale, octree_resolution, remove_background)` — returns `mesh_url`
- `generate_trellis_2(image, seed, pipeline_type, generate_model, generate_video, texture_size, decimation_target, ...)` — returns `model_url` + `video_url`

### `src/utils.py`

- `format_cost(cost: float) -> str` — `$0.42` or `< $0.01` for negligible amounts
- `format_duration(seconds: float) -> str` — `5.3s`, `2.1m`, `1.5h`
- `format_timestamp(ts: str) -> str` — truncates ISO timestamp to `YYYY-MM-DD HH:MM`

### `app.py` (Streamlit UI)

**Startup flow**:
1. `st.set_page_config()` — wide layout, page title/icon
2. `check_token()` — shows error message and `st.stop()` if `.env` missing
3. `init_db()` — creates SQLite database if first run
4. Render title and three tabs

**Video Tab**:
1. Model selector (dropdown with display names, index-based lookup)
2. `_render_generation_form(model)` — renders Balanced + Advanced params
3. On "Generate Video" click:
   - Validates model-specific required inputs (Seedance image is optional; I2V image is required)
   - Opens `st.status` progress block
   - Dispatches to correct `generate_*()` function
   - On success: `st.video(url)`, download link, metrics (predict time + cost)
   - On failure: `st.error()` + `st.toast()`

**3D Tab**:
1. Same layout as Video tab
2. On success: `<model-viewer>` inline 3D viewer via `st.components.v1.html()` + optional video preview (TRELLIS 2)
3. Download link for the 3D model file

**History Tab**:
1. Summary cards (total generations, total cost, avg predict time)
2. Per-model expandable breakdown (cost + avg time per model)
3. Recent generations table (pandas DataFrame, newest first, 50 rows max) with filters/search and temporary output links
4. Columns shown: Timestamp, Model, Type, Prompt, Predict Time, Est. Cost, Status

**`_render_generation_form(model)` helper**:
- Renders prompt text area (if `supports_text`) or info message
- Renders image uploader (if `supports_image`) — stores as `_uploaded_image` in kwargs dict
- Iterates `model.balanced_params`: duration slider, seed input, aspect_ratio select, resolution select, pipeline_type select, generic fallback for bool/int/float/str
- Advanced params in `st.expander("⚙️ Advanced Parameters")`: same fallback logic
- Returns `dict` of kwargs on generate button click, or `None` if not clicked
- Validates: prompt/image requirements separately from model capabilities, so dual-mode models can run text-only where supported

---

## Generation Flow (End-to-End)

```
User selects model → fills params → clicks Generate
    │
    ├─ app.py validates inputs
    ├─ Calls dispatch: if video → video_gen.generate_*()
    │                  if 3d    → threed_gen.generate_*()
    │
    ├─ generate_*() builds input dict from kwargs
    ├─ replicate.predictions.create(model, input)
    ├─ Poll prediction status until Replicate finishes
    ├─ Extracts/normalizes output URL + metrics
    ├─ Calculates cost via pricing.py
    ├─ Records to SQLite via cost_tracker.py
    └─ Returns result dict back to app.py
    │
    ├─ app.py displays:
    │   ├─ st.video(url) or model-viewer HTML
    │   ├─ Download link (markdown)
    │   ├─ Predict time metric
    │   └─ Estimated cost metric
    │
    └─ History tab reads from SQLite (no Replicate API calls)
```

---

## Cost Tracking Details

**Pricing is static** — no per-generation API calls for pricing.

| Model | Hardware | Compute $/s | Output $/s | Typical cost (5s video) |
|-------|----------|-------------|------------|--------------------------|
| Wan 2.7 T2V | A100-80GB | $0.00140 | $0.10 | ~$0.50 |
| Wan 2.5 I2V Fast | A100-80GB | $0.00140 | $0.05 | ~$0.25 |
| Seedance 2.0 | A100-80GB | $0.00140 | $0.15 | ~$0.75 |
| Hunyuan3D 2.0 | L40S | $0.000575 | — | $0.03–0.30 |
| TRELLIS 2 | A100-80GB | $0.00140 | — | $0.10–1.00 |

For video models, cost is calculated as `output_duration × per_second_output_price` (since Replicate bills by output seconds, not compute time). For 3D models, cost is `predict_time × hardware_price_per_second`.

Database stores `estimated_cost_usd` as a float for each generation. History tab aggregates: total cost per model and overall.

---

## Key Design Decisions Implemented

| # | Decision | Implementation |
|---|----------|---------------|
| 1 | No autosave / no local file storage | Preview from Replicate URL; download = browser download; no `outputs/` directory |
| 2 | All params exposed | Balanced (always visible) + Advanced (in `st.expander`) |
| 3 | Tabbed UI | `st.tabs(["🎥 Video", "🧊 3D", "📊 History"])` |
| 4 | Static pricing table | `pricing.py` — hardcoded dict, updated manually or via future cron job |
| 5 | SQLite history | `cost_tracker.py` — stores metadata, not files; survives app restarts |
| 6 | Index-based model selection | No fragile display_name → name matching; uses `format_func` lambda |
| 7 | `.env` for secrets | `python-dotenv` loads `REPLICATE_API_TOKEN`; `.env.example` provided as template |
| 8 | Graceful token-missing UX | `check_token()` called at startup; app shows clear instructions instead of crashing |
| 9 | `src/` source layout | All library code under `src/`; `app.py` at root with `sys.path.insert` |
| 10 | uv for package management | `pyproject.toml` with uv-compatible deps |

---

## Dependencies

From `pyproject.toml`:

```toml
dependencies = [
    "streamlit>=1.58.0",     # Web UI
    "replicate>=1.0.7",      # Replicate API client
    "python-dotenv>=1.2.2",  # .env loading
    "pillow>=10.0.0",        # Image handling
    "requests>=2.31.0",      # HTTP (used by replicate client)
    "pandas>=2.0.0",         # History table display
]

[project.optional-dependencies]
dev = [
    "ruff>=0.4.0",           # Linting
    "black>=24.0.0",         # Formatting
]
```

---

## What Is NOT Implemented (Future Versions)

Per `ROADMAP.md`:

1. **Model capability matrix + schema-driven UX** — planned for v0.3.0
2. **Durable output storage + permanent History preview** — planned for v0.4.0
3. **Automated tests + optional live Replicate smoke tests** — planned for v0.5.0
4. **Expanded model catalogue** — planned after schema/capability handling is solid

---

## Quick Start

```bash
cd /home/tima/ai_generation_ui
cp .env.example .env              # add REPLICATE_API_TOKEN=r8_your_token
uv venv
uv pip install -e .
uv run streamlit run app.py       # open http://localhost:8501
```
