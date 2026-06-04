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

**SELECTED: Hunyuan3D 2.0 + Hunyuan 3D 3.1 + Microsoft TRELLIS 2**

| Model | Type | Notes |
|---|---|---|
| Hunyuan3D 2.0 | Image-to-3D in current Replicate schema | Existing image-driven mesh generation model; requires versioned Replicate prediction path. |
| Hunyuan 3D 3.1 | Text-to-3D or Image-to-3D | Implemented in v0.4.0 and patched in v0.4.1/v0.4.2; newer Tencent model with texture fidelity and geometry precision; Replicate schema accepts exactly one of prompt or image, and image inputs are sent as explicit image data URIs to avoid extensionless upload URLs. |
| TRELLIS 2 | Image-to-3D | PBR textures, up to 1536³, open-source; requires versioned Replicate prediction path. |

**Rationale**: Hunyuan 3D 3.1 is the newer Hunyuan option and should be added in v0.4.0 because it expands 3D from image-only to text-or-image generation while staying within the hosted 3D scope. Hunyuan3D 2.0 and TRELLIS remain useful existing options. Text-to-3D is now planned specifically through verified provider schemas such as `tencent/hunyuan-3d-3.1`, not as a generic unsupported promise.

**Not selected**: Tripo 2.5, Rodin

---

## Decision 3: UI Layout

**SELECTED: Top-level destinations with query-param-backed segmented navigation**

Top-level destinations today: **Video** | **3D** | **History**. **v0.9.0** adds **Audio** (music + speech) before v1.0.0.

The app uses segmented navigation backed by query params instead of top-level `st.tabs`. This lets deep links such as `?page=history` and History preview selections stay on the correct page instead of resetting to Video on rerun.

History itself uses a `Gallery` / `Records` segmented view selector that redraws exactly one body at a time, rather than rendering both tab bodies as nested content.

---

## Decision 4: Output Display

**SELECTED: Option C — Inline viewer + automatic local copy**

- Video: `st.video(url)` inline player using the provider output URL or saved local file when available.
- 3D: `<model-viewer>` inline using the provider output URL or saved local file when available.
- Successful outputs are automatically saved under `outputs/videos/` or `outputs/models_3d/`.
- History stores both the provider URL and local file metadata.
- History distinguishes local files, missing local files, and temporary provider links.
- History Gallery cards can preview saved outputs inline, download local files, and open local outputs in the desktop file finder when available.
- Provider URLs remain useful for immediate preview, but may expire after ~1 hour.

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

**SELECTED: Inline viewer + automatic local copy**

**Flow**:
1. Replicate API returns an ephemeral output URL
2. Inline viewer shows the output directly from that URL (video: `st.video(url)`, 3D: `<model-viewer src=url>`)
3. Successful outputs are automatically saved under `outputs/videos/` or `outputs/models_3d/`
4. History stores both the provider URL and local file metadata
5. History distinguishes local files, missing local files, and temporary provider links
6. Provider URLs remain useful for immediate preview, but may expire after ~1 hour

**Rationale**: This keeps the immediate preview experience simple while also preserving durable local copies and honest History metadata for later review or download.

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

## Decision 11: Replicate Prediction Endpoint Mode

**SELECTED: Use the endpoint mode required by each model**

- Versionless-capable models can use `replicate.predictions.create(model=model_id, input=...)`.
- Models that do not support versionless predictions must resolve `latest_version.id` and use `replicate.predictions.create(version=version_id, input=...)`.
- Hunyuan3D 2.0 and TRELLIS 2 currently use the versioned path in the 3D generation wrapper.
- Hunyuan 3D 3.1 (`tencent/hunyuan-3d-3.1`) is planned for v0.4.0 and Replicate's API page reports `usesVersionlessApi: true`, so it should use the versionless model prediction path.

**Rationale**: Replicate model pages can exist while their versionless prediction endpoints return 404. Using each model's supported endpoint mode prevents avoidable paid-call failures and keeps model compatibility explicit.

---

## Decision 12: Provider Expansion

**SELECTED: Add fal.ai through a provider adapter layer, not direct UI branches**

- Current implementation remains Replicate-only.
- fal.ai development starts after the v1.0.0 Replicate-only baseline; v0.x and v1.0.0 remain Replicate-only implementation/release work.
- Provider should be visible in model cards, History, dry-run payloads, diagnostics, and errors, but model selection should remain workflow/use-case first.
- Missing credentials for one provider should not block using the other provider.
- NVIDIA Cosmos 3 Super Image to Video (`nvidia/cosmos-3-super/image-to-video`) is the first documented fal.ai image-to-video candidate for post-v1.0 work.
- Meshy is a post-v1.0 fal.ai/provider-expansion candidate.
- Additional fal.ai model IDs, schemas, output shapes, and pricing must be verified from fal.ai model pages/OpenAPI before adding real fal.ai models.

**Rationale**: Provider expansion is useful, but the app is a personal creative UI rather than an API console. A thin provider layer keeps Replicate/fal.ai differences manageable while preserving plain-English UX.

---


## Decision 13: Pre-v1 Architecture Stabilization

**SELECTED: Use v0.4.3–v0.4.9 for architecture cleanup before adding more user-facing features**

- Keep v0.4.x behavior Replicate-only.
- Do not implement fal.ai in v0.4.x.
- Split Streamlit UI code out of `app.py` before adding more UI features.
- Introduce shared domain/result types before richer History, dry-run previews, or provider expansion.
- Make the model catalogue provider-aware while all current models still use Replicate.
- Extract Replicate SDK behavior into a provider adapter before adding another provider.
- Normalize outputs as typed assets so single-output and multi-output models share one path.
- Make History provider-aware and named-field/typed-record based before adding reuse, filters, or fal.ai.

**Rationale**: The current v0.4.2 implementation works, but too many responsibilities are concentrated in `app.py` and the generation wrappers. Sorting out presentation/service/provider/storage/history boundaries now is less risky than doing it after dry-run tooling, plain-English UX, History reuse, or fal.ai support have added more coupling.

Detailed plan: `IMPLEMENTATION_PLAN_ARCHITECTURE_REFACTOR.md`.

---

## Final Model List

Authoritative counts: **CHANGELOG.md** (shipped), **IMPLEMENTATION_VER-0.9.0.md** (planned audio).

### Video Models (11 — Replicate, v0.6.10)

| Replicate ID | Role |
|---|---|
| `wan-video/wan-2.7-t2v` | Text-to-video |
| `wan-video/wan-2.5-i2v-fast` | Image-to-video |
| `bytedance/seedance-2.0` | T2V / I2V |
| `bytedance/seedance-2.0-fast` | Faster multimodal T2V / I2V |
| `alibaba/happyhorse-1.0` | T2V / I2V |
| `runwayml/gen-4.5` | T2V / I2V |
| `kwaivgi/kling-v3-omni-video` | Multimodal |
| `bytedance/dreamactor-m2.0` | Motion transfer |
| `runwayml/aleph-2` | Video edit |
| `kwaivgi/kling-v3-motion-control` | Motion transfer |
| `kwaivgi/kling-o1` | Multimodal / edit |

**Post-1.0 UI**: Aleph keyframes — see Decision below and `ROADMAP.md`. Multi-reference uploads were resolved in v0.6.11 for metadata-marked multi-file params.

**Post-1.0 provider**: `nvidia/cosmos-3-super/image-to-video` via fal.ai.

### 3D / texture Models (7 — Replicate)

| Replicate ID | Role |
|---|---|
| `tencent/hunyuan3d-2` | Image-to-3D; versioned |
| `tencent/hunyuan3d-2mv` | Multiview image-to-3D; versioned (v0.6.5) |
| `fishwowater/trellis2` | Image-to-3D (PBR + preview); versioned |
| `tencent/hunyuan-3d-3.1` | Text-to-3D or image-to-3D; versionless |
| `adirik/text2tex` | Mesh texturing (.obj + prompt); versioned (v0.6.5) |
| `adirik/texture` | Mesh texturing (mesh + prompt); versioned (v0.6.5) |
| `hyper3d/rodin` | Text-to-3D (+ optional reference); versioned (v0.6.5) |

### Audio Models (9 — planned v0.9.0, not implemented)

**Music**: `minimax/music-2.5`, `stability-ai/stable-audio-2.5`, `google/lyria-2`.

**Speech**: `inworld/realtime-tts-2`, `inworld/realtime-tts-1.5-max`, `minimax/speech-2.8-hd`, `minimax/speech-2.8-turbo`, `resemble-ai/chatterbox`, `elevenlabs/v3`.

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

---

## Decision: advanced Aleph keyframe UI → post-1.0.0

**Date**: 2026-06-04 (recorded after v0.6.10 completion; updated after v0.6.11 multi-reference upload support)

**Deferred intentionally (not v1.0.0 blockers)**:

1. **Aleph 2.0 keyframes** — UI for paired `keyframe_images` + `keyframe_positions`. v0.6.10 ships source video + edit prompt only, and v0.6.11 keeps keyframe controls deferred.

**Resolved in v0.6.11**: multi-reference upload controls for `reference_images`, `reference_videos`, `reference_audios`, and Rodin `images` are no longer deferred; the UI supports multi-file upload controls where the model metadata marks those params as multi-file.

**Rationale**: Reduce risk of invalid paid calls and UI clutter before the Replicate-only personal baseline (v1.0.0). Aleph remains usable without keyframes; that power-user flow can wait until after v1.0.

**Planned milestone**: Post-1.0 — see `ROADMAP.md` section “Advanced video inputs”. Not part of v0.7.0–v0.8.0 unless explicitly reprioritized.

---

## Decision: Audio models before v1.0.0 (v0.9.0)

**Date**: 2026-06-04

**Scope**: Add Replicate **music** and **speech** models before declaring v1.0.0, as milestone **v0.9.0** (after v0.7.0, before v0.8.0 smoke QA).

**Music**: `minimax/music-2.5`, `stability-ai/stable-audio-2.5`, `google/lyria-2`.

**Speech**: `inworld/realtime-tts-2`, `inworld/realtime-tts-1.5-max`, `minimax/speech-2.8-hd`, `minimax/speech-2.8-turbo`, `resemble-ai/chatterbox`, `elevenlabs/v3`.

**Rationale**: Personal studio should cover video, 3D, and audio before the Replicate-only v1.0 baseline; fal.ai remains post-1.0.

**Details**: `IMPLEMENTATION_VER-0.9.0.md`, `ROADMAP.md` v0.9.0.
