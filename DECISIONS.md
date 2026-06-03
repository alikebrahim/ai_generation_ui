# DECISIONS.md — Resolved Decisions

All decisions have been made. This document records the final choices and rationale.

---

## Decision 1: Video Models

**SELECTED: Wan 2.7 T2V + Wan 2.5 I2V Fast (Option A) AND Seedance 2.0 (Option B)**

| Model | Type | Price | Speed | Notes |
|---|---|---|---|---|
| Wan 2.7 T2V | Text-to-Video | ~$0.14-0.30/video | Fast (5.24s/1s) | Best value, open-source |
| Wan 2.5 I2V Fast | Image-to-Video | ~$0.14-0.30/video | Fast | Speed-optimized |
| Seedance 2.0 | T2V + I2V | Moderate-high | Moderate | Multi-reference, continuation, lip-sync |

**Rationale**: Wan covers daily experimentation (cheap, fast). Seedance covers advanced workflows (multi-reference images, video continuation, character consistency). Together they span simple to complex use cases.

**Archived for future**: Grok Imagine Video, Kling 3.0, Runway Gen-4.5, Hailuo 2.3

---

## Decision 2: 3D Models

**SELECTED: Hunyuan3D 2.0 (Option A) + Microsoft TRELLIS 2 (Option B)**

| Model | Type | Notes |
|---|---|---|
| Hunyuan3D 2.0 | Image-to-3D in current Replicate schema | Best quality image-driven mesh generation |
| TRELLIS 2 | Image-to-3D | PBR textures, up to 1536³, open-source |

**Rationale**: The current Replicate Hunyuan3D schema is image-only, so current 3D scope is Image-to-3D. TRELLIS 2 complements it with high-res PBR textured assets. Both accept Midjourney art or other clear subject images as input. Text-to-3D remains future scope unless a reliable Replicate text-capable model is added.

**Not selected**: Tripo 2.5, Rodin

---

## Decision 3: UI Layout

**SELECTED: Option A — Tabbed Interface**

Tabs: **Video** | **3D** | **History**

Clean separation, each tab self-contained, standard Streamlit pattern.

---

## Decision 4: Output Display

**SELECTED: Option C — Inline viewer + download button (both video and 3D)**

- Video: `st.video(url)` inline player using Replicate output URL directly
- 3D: `<model-viewer>` inline using Replicate output URL directly
- Download button: triggers browser download from the Replicate URL
- No local file is saved unless the user explicitly downloads
- Outputs are ephemeral; Replicate URLs expire after ~1 hour

---

## Decision 5: Model Parameter Exposure

**SELECTED: Option C (All params) — with TWO categories**

Parameters are split into two clearly separated categories:

**Balanced (always visible)**:
- Prompt
- Duration / resolution
- Seed
- Aspect ratio
- Negative prompt (where supported)

**Advanced (in collapsible expander)**:
- Guidance scale / CFG
- Number of inference steps
- Scheduler type
- Motion strength
- Any model-specific technical params

This gives full control without overwhelming casual users. The Balanced set covers 90% of use cases; Advanced is there when needed.

---

## Decision 6: Error Handling & User Feedback

**SELECTED: Option C — Toast + inline status**

- `st.toast()` for: "Generation started", "Generation complete", quick errors
- Inline in generation area: progress bar, ETA, detailed error messages, cost display

---

## Decision 7: File Management

**SELECTED: Preview-only — no local file storage**

**Flow**:
1. Replicate API returns an ephemeral output URL
2. Inline viewer shows the output directly from that URL (video: `st.video(url)`, 3D: `<model-viewer src=url>`)
3. User clicks Download button to save to their browser's default Downloads folder
4. No file is automatically saved to disk on the server
5. Replicate URLs expire after ~1 hour; after that the output is no longer viewable
6. Metadata (prompt, params, cost, timestamp, replicate_url) is preserved in SQLite history

**Rationale**: Prevents redundant disk usage. Autosave + download do the same thing. Preview works from URL without saving. The user saves only when they want to keep the output.

---

## Decision 8: API Token Management

**SELECTED: Option A — .env file with python-dotenv**

- `.env` file (gitignored) stores `REPLICATE_API_TOKEN`
- `.env.example` provided as template
- Loaded at app startup via `python-dotenv`

---

## Decision 9: Cost Tracking

**SELECTED: Option C — Static pricing table, fetched once**

**Implementation**:
1. On first run, fetch hardware info per model via `replicate.models.get()`
2. Build a static pricing table in `src/pricing.py` (hardcoded dict)
3. Calculate cost: `cost = predict_time * price_per_second`
4. Store in SQLite database alongside generation metadata
5. Display as "Estimated cost: $0.25" in History tab

**Key constraint**: No per-generation API calls for pricing. The table is built once and updated manually (or via cron job later). Pricing is fetched at setup time, not at runtime.

**Future**: Set up a quarterly cron job to refresh the pricing table.

---

## Decision 10: Package Management

**SELECTED: Option A — uv (Astral)**

```bash
uv venv                    # Create .venv with Python 3.11+
uv pip install -e .        # Install project dependencies
uv run streamlit run app.py # Run the app
```

---

## Final Model List

### Video Models (3)
1. `wan-video/wan-2.7-t2v` — Text-to-Video
2. `wan-video/wan-2.5-i2v-fast` — Image-to-Video
3. `bytedance/seedance-2.0` — T2V + I2V (multi-reference)

### 3D Models (2)
4. `tencent/hunyuan3d-2` — Image-to-3D
5. `fishwowater/trellis2` — Image-to-3D (PBR)

---

## Implementation Plan

### Phase 0: Project Bootstrap
1. Initialize uv project (`uv init` if needed, verify pyproject.toml)
2. Create `.env` from `.env.example`
3. Create `.gitignore` (env, venv, outputs, data, pycache)
4. Verify `uv pip install -e .` works

### Phase 1: Core Infrastructure
5. Create `src/config.py` — load .env, define paths, constants
6. Create `src/pricing.py` — static pricing table for all 5 models
7. Create `src/models_config.py` — model identifiers, parameter schemas, balanced/advanced param definitions
8. Create `src/cost_tracker.py` — SQLite database (init, insert, query, aggregate stats)
9. Create `src/utils.py` — file download, filename generation, prompt hashing

### Phase 2: Video Generation
10. Create `src/video_gen.py` — generate functions for Wan 2.7 T2V, Wan 2.5 I2V Fast, Seedance 2.0
11. Each function: accept params → call Replicate → poll status → download output → record in DB → return result

### Phase 3: 3D Generation
12. Create `src/threed_gen.py` — generate functions for Hunyuan3D 2.0, TRELLIS 2
13. Same pattern as video: accept params → call Replicate → poll → download → record → return

### Phase 4: Streamlit UI
14. Create `app.py` — main entry point with tab layout
15. Video tab: model selector → input form (balanced params visible, advanced in expander) → generate → progress → display (st.video + download) → show cost
16. 3D tab: same pattern with model-viewer instead of st.video
17. History tab: summary stats (total spend, count per model) + filterable table of past generations + re-open links

### Phase 5: Polish
18. Error handling: toast + inline errors, retry logic for transient failures
19. Test end-to-end with sample prompts for each model
20. Verify cost tracking accuracy
