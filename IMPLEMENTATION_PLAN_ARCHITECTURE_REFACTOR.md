# v0.4.3–v0.4.9 Architecture Stabilization Plan

> **For Hermes:** Use `subagent-driven-development` only when executing this plan task-by-task. Do not run paid Replicate/fal.ai predictions unless the user explicitly authorizes provider, model, expected cost, and scope.

**Goal:** Refactor the current v0.4.2 Replicate-only app into a cleaner, provider-aware architecture before adding more features, so future dry-run tooling, plain-English UX polish, History reuse, and eventual fal.ai support can be developed without repeatedly touching fragile `app.py` branches.

**Architecture:** Keep behavior Replicate-only through v0.4.9, but separate Streamlit presentation, model metadata, generation orchestration, provider-specific execution, output storage, and History persistence. Use battle-tested lightweight patterns rather than heavy frameworks: presentation/service/provider-adapter boundaries, typed dataclasses for results/assets, registry-based dispatch as an incremental bridge, and SQLite repository-style history functions.

**Tech Stack:** Python 3.11+, Streamlit, Replicate Python client, SQLite, uv, ruff/black. No new runtime dependency is expected for this refactor.

---

## Online research assessment

No online research is required for v0.4.3–v0.4.9 implementation.

Reasoning:

- The work is an internal architecture refactor of known code, not a provider/schema discovery task.
- The desired design is already documented in `ROADMAP.md`, `DECISIONS.md`, and `IMPLEMENTATION_PLAN_PROVIDER_EXPANSION.md`.
- The patterns needed are stable and generic:
  - Streamlit UI module separation.
  - Service layer around app actions.
  - Provider adapter/ports-and-adapters boundary.
  - Typed result dataclasses.
  - Repository-style SQLite access functions.
- Fetching provider docs now could distract from the goal because fal.ai implementation remains out of scope for v0.x.

Use online/provider documentation only when a milestone actually depends on current external facts:

- v0.5.0 schema diagnostics may query Replicate metadata non-paid.
- post-v1.0 fal.ai implementation must re-check fal.ai OpenAPI, upload behavior, output shape, and pricing before any real model is added.
- Pricing refresh work should use current provider pricing docs/API if available.

---

## Version breakdown

The architecture work should stay in v0.4.x patch releases because it intentionally preserves the current Replicate-only product behavior. The user-facing capability set should not materially expand until v0.5.0.

| Version | Theme | Main outcome |
|---|---|---|
| v0.4.3 | UI module split | `app.py` becomes a thin Streamlit shell; tabs/forms/result views move under `src/ui/`. |
| v0.4.4 | Generation registry + domain types | Model dispatch leaves `app.py`; shared request/result/asset dataclasses are introduced without changing behavior. |
| v0.4.5 | Provider-aware model metadata | Current Replicate models get provider/provider endpoint metadata; endpoint mode moves into catalogue data. |
| v0.4.6 | Replicate adapter extraction | Replicate prediction creation, polling, output normalization, and friendly errors move behind `ReplicateAdapter`. |
| v0.4.7 | Output asset + storage service | Videos, 3D models, and previews are normalized as assets and saved through one output-storage service. |
| v0.4.8 | Provider-aware History service | SQLite history gains provider/job/asset fields and UI reads typed history records instead of raw tuple positions. |
| v0.4.9 | Integration hardening + dry-run foundation | Refactored architecture is cleaned up, legacy shims reduced, docs aligned, and v0.5 dry-run work has a clear service hook. |

---

## Guardrails for every patch

- Preserve current user-visible workflows unless the patch explicitly says otherwise:
  - text-to-video
  - image-to-video
  - image-to-3D
  - Hunyuan 3D 3.1 text-to-3D
- Keep fal.ai implementation out of v0.4.x.
- Do not run paid predictions during refactor verification.
- Prefer compatibility shims over risky all-at-once rewrites.
- Keep each patch releasable on its own.
- After each patch, run:

```bash
uv run python -m compileall -q app.py src
uv run ruff check .
```

- For patches touching History, also run a local SQLite probe against a temporary DB or carefully isolated migration path.
- Update only docs that materially changed. At minimum, update `CHANGELOG.md`, `ROADMAP.md`, and the relevant implementation notes when marking a patch complete.

---

## v0.4.3 — UI Module Split

**Goal:** Reduce `app.py` from a large mixed-responsibility file into a thin app shell while preserving current behavior.

**Files:**

- Modify: `app.py`
- Create: `src/ui/__init__.py`
- Create: `src/ui/forms.py`
- Create: `src/ui/video_tab.py`
- Create: `src/ui/threed_tab.py`
- Create: `src/ui/history_tab.py`
- Create: `src/ui/result_views.py`
- Create: `src/ui/model_viewer.py`

**Tasks:**

1. Create `src/ui/` package with empty `__init__.py`.
2. Move `_friendly_label`, `_render_param_widget`, and `_render_generation_form` from `app.py` to `src/ui/forms.py`.
3. Move video result display code into `src/ui/result_views.py`.
4. Move 3D result display and `<model-viewer>` HTML creation into `src/ui/model_viewer.py` / `src/ui/result_views.py`.
5. Move Video tab body into `src/ui/video_tab.py`.
6. Move 3D tab body into `src/ui/threed_tab.py`.
7. Move History tab body, `_mime_for_path`, and `_safe_local_path` into `src/ui/history_tab.py`.
8. Keep existing generation dispatch inside the tab modules for now; do not introduce provider abstractions in this patch.
9. Reduce `app.py` to page setup, token check, DB init, title, tabs, and calls to `render_video_tab()`, `render_3d_tab()`, and `render_history_tab()`.
10. Run compile and ruff.
11. Manually launch Streamlit if feasible and confirm all tabs still render.

**Acceptance criteria:**

- `app.py` is primarily composition, not implementation detail.
- No generation behavior changes.
- No database schema changes.
- Compile and ruff pass.

---

## v0.4.4 — Generation Registry + Domain Types

**Goal:** Remove model-name dispatch from UI modules and introduce shared internal result shapes as a stepping stone toward provider adapters.

**Files:**

- Create: `src/domain.py`
- Create: `src/generation_registry.py`
- Modify: `src/ui/video_tab.py`
- Modify: `src/ui/threed_tab.py`
- Modify: `src/video_gen.py` only if needed for adapter helpers
- Modify: `src/threed_gen.py` only if needed for adapter helpers

**Tasks:**

1. Add lightweight dataclasses in `src/domain.py`:
   - `OutputAsset`
   - `CostEstimate`
   - `GenerationResult`
   - optional `GenerationRequest`
2. Keep dataclasses permissive enough to wrap current dict result values; avoid forcing a full rewrite in this patch.
3. Add `src/generation_registry.py` with `GENERATION_HANDLERS` mapping model slug to current generation function.
4. Add `run_generation(model, params, progress_callback=None)` that looks up and invokes the handler.
5. Replace `if model.name == ...` dispatch in UI tab modules with `run_generation()`.
6. Preserve current result dict handling in result views, or add a small compatibility adapter that accepts either dicts or `GenerationResult`.
7. Run compile and ruff.
8. Add a non-paid probe that imports all handlers and confirms every configured model has a handler.

**Acceptance criteria:**

- UI modules no longer contain per-model generation `if/elif` chains.
- Every current model maps to exactly one generation handler.
- No provider abstraction is required yet.
- Compile, ruff, and handler registry probe pass.

---

## v0.4.5 — Provider-Aware Model Metadata

**Goal:** Make current Replicate-only models explicit provider-aware catalogue entries before adding provider adapters.

**Files:**

- Modify: `src/models_config.py`
- Modify: `src/pricing.py`
- Modify: `src/validation.py` only if naming changes require it
- Modify: `src/generation_registry.py`
- Modify docs if the metadata shape changes materially

**Tasks:**

1. Add provider typing to `src/models_config.py`:
   - `ProviderName = Literal["replicate", "fal"]`
   - `provider: ProviderName`
   - `provider_model_id: str`
   - `provider_endpoint: dict[str, Any]`
2. Keep a compatibility property or alias for `replicate_id` during the transition if that reduces churn.
3. Set every current model to `provider="replicate"`.
4. Record Replicate endpoint mode in metadata:
   - versionless for current video models and Hunyuan 3D 3.1
   - versioned for Hunyuan3D 2.0 and TRELLIS 2
5. Begin moving UI-specific media role metadata into `ModelConfig` where straightforward:
   - subject image
   - start frame image
   - text description vs subject image for Hunyuan 3D 3.1
6. Update `src/pricing.py` to accept `provider_model_id` or continue supporting Replicate IDs through compatibility helpers.
7. Run compile and ruff.
8. Add a non-paid probe that every model has provider metadata and a valid endpoint mode.

**Acceptance criteria:**

- Current model catalogue is provider-aware but still Replicate-only.
- Endpoint mode is data, not hidden inside generation code.
- Existing UI/generation behavior remains intact.
- Compile, ruff, and provider metadata probe pass.

---

## v0.4.6 — Replicate Adapter Extraction

**Goal:** Move Replicate-specific execution details behind a provider adapter while preserving current generation behavior.

**Files:**

- Create: `src/providers/__init__.py`
- Create: `src/providers/base.py`
- Create: `src/providers/replicate.py`
- Modify: `src/video_gen.py`
- Modify: `src/threed_gen.py`
- Modify: `src/utils.py` if Replicate output normalization/friendly errors move
- Modify: `src/config.py` only if credential status is introduced here

**Tasks:**

1. Define provider adapter protocol/base types in `src/providers/base.py`:
   - credential status
   - create prediction
   - poll prediction
   - normalize output
   - friendly error
2. Implement `ReplicateAdapter` in `src/providers/replicate.py`.
3. Move duplicated `_run_prediction()` logic from `video_gen.py` and `threed_gen.py` into the adapter.
4. Move `_latest_version_id()` into the adapter and drive versioned/versionless creation from model metadata.
5. Move `output_to_url()` or wrap it as Replicate output normalization if it is provider-specific enough.
6. Move Replicate-specific friendly error copy out of generic `utils.py` or expose it through the adapter.
7. Update video/3D generation wrappers to call the adapter instead of direct `replicate.predictions.create(...)`.
8. Run compile and ruff.
9. Add a non-paid probe using monkeypatched/fake adapter calls if practical to verify versioned vs versionless branch selection without creating predictions.

**Acceptance criteria:**

- Direct Replicate SDK calls are isolated in `src/providers/replicate.py`.
- Generation wrappers no longer decide versioned vs versionless prediction creation themselves.
- No paid calls are run during verification.
- Compile, ruff, and non-paid branch probe pass.

---

## v0.4.7 — Output Asset + Storage Service

**Goal:** Normalize provider outputs as typed assets and centralize local downloading/storage.

**Files:**

- Create: `src/services/__init__.py`
- Create: `src/services/output_storage.py`
- Modify: `src/domain.py`
- Modify: `src/video_gen.py`
- Modify: `src/threed_gen.py`
- Modify: `src/ui/result_views.py`
- Modify: `src/ui/history_tab.py` only if local download helpers move
- Modify: `src/utils.py` to remove or delegate `download_output()` if appropriate

**Tasks:**

1. Finalize `OutputAsset` fields:
   - `kind`
   - `provider_url`
   - `local_path`
   - `mime_type`
   - `file_size_bytes`
   - `label`
2. Create `src/services/output_storage.py` with `download_asset()` and `download_assets()` helpers.
3. Move extension/MIME detection and local file naming out of generic `utils.py` if practical.
4. Update video generation to produce a video asset.
5. Update Hunyuan/Hunyuan3D generation to produce a 3D model asset.
6. Update TRELLIS to produce model and preview-video assets.
7. Keep old result keys such as `url`, `model_url`, and `video_url` temporarily if UI/history still need them.
8. Update result views to prefer assets when available.
9. Run compile and ruff.
10. Add a local non-network probe for asset serialization and MIME detection.

**Acceptance criteria:**

- Output handling no longer assumes a single URL per generation.
- TRELLIS preview video and model output fit the same asset model.
- Local file metadata is attached to assets.
- Compile, ruff, and local asset probe pass.

---

## v0.4.8 — Provider-Aware History Service

**Goal:** Make History provider-aware and less tuple-position fragile before fal.ai or richer History features are added.

**Files:**

- Create: `src/history_service.py`
- Modify: `src/cost_tracker.py`
- Modify: `src/domain.py`
- Modify: `src/video_gen.py`
- Modify: `src/threed_gen.py`
- Modify: `src/ui/history_tab.py`

**Tasks:**

1. Add provider-aware columns through migration in `src/cost_tracker.py`:
   - `provider`
   - `provider_model_id`
   - `provider_job_id`
   - `provider_job_url`
   - `output_assets_json`
2. Keep `replicate_url` for backward compatibility while current rows and UI still use it.
3. Add typed history row/dataclass in `src/domain.py` or `src/history_service.py`.
4. Add `record_generation_result(result)` that stores provider fields and asset JSON.
5. Keep existing `record_generation()` as a compatibility wrapper if needed.
6. Keep the existing History UI tuple API compatible and add typed provider-aware reads for follow-up UI filters.
7. Add Provider as a visible History filter/column if it fits cleanly; otherwise add the stored field and defer UI filter to v0.5+.
8. Run compile and ruff.
9. Run a local SQLite migration probe against a temporary DB:
   - fresh schema initialization
   - legacy schema migration
   - insert/read with provider fields

**Acceptance criteria:**

- Existing History rows remain readable.
- New rows can store provider/job/assets metadata.
- Existing tuple-position History UI remains compatible; provider-aware typed queries are available for follow-up UI filters.
- Compile, ruff, and migration probe pass.

---

## v0.4.9 — Integration Hardening + Dry-Run Foundation

**Goal:** Finish the architecture stabilization series and leave v0.5.0 ready to add request preview/dry-run safety features cleanly.

**Files:**

- Modify: `src/generation_service.py` or create it if not already created
- Modify: `src/ui/forms.py`
- Modify: `src/ui/video_tab.py`
- Modify: `src/ui/threed_tab.py`
- Modify: `src/providers/base.py`
- Modify: `src/providers/replicate.py`
- Modify docs:
  - `README.md`
  - `CHANGELOG.md`
  - `ROADMAP.md`
  - `DECISIONS.md`
  - this implementation plan if reality diverged

**Tasks:**

1. Introduce or finalize `src/generation_service.py` as the single orchestration entry point for UI:
   - validate params
   - build provider request/payload
   - run generation
   - store outputs
   - record History
2. Add a non-paid `prepare_generation_request()` or equivalent service hook that returns provider, model, mode, sanitized params, estimated/unknown cost, and payload summary without creating a prediction.
3. Do not build the full UI dry-run feature yet; that belongs in later safety/dry-run work after the v0.5 UI/UX pass.
4. Remove obsolete duplicate helpers only when compile/lint/local probes prove they are unused.
5. Re-check user-facing behavior in Video, 3D, and History tabs.
6. Update docs to mark v0.4.3–v0.4.9 complete only as each patch lands.
7. Run compile and ruff.
8. Run accumulated local probes for registry, provider metadata, asset serialization, and History migration.

**Acceptance criteria:**

- UI calls a generation service, not provider/generation wrappers directly.
- A clean no-paid-call request-preparation hook exists for later safety/dry-run work.
- v0.4.x remains Replicate-only in behavior.
- Docs clearly distinguish architecture stabilization from new provider implementation.
- Compile, ruff, and all local probes pass.

---

## After v0.4.9

After this series, resume feature work:

- v0.5.0-v0.5.10: Minimal UI/UX, nicer navigation/header, focused generation panels, media-role forms, thumbnails/previews, gallery-first History, separate Gallery/Records views, and inline History previews.
- v0.6.0: Generation safety, dry-run payload previews, schema drift checks.
- v0.7.0: Better errors, progress, and recovery.
- v0.6.0: Safety, metadata audit, dry-run payloads, and schema diagnostics.
- v0.6.5: Verified Replicate 3D/texture model expansion.
- v0.7.0: Better errors, progress, and recovery.
- v0.8.0: Replicate audio (music + speech); v1.0.0 personal baseline follows.
- v1.0.0: Stable Replicate-only personal local release. fal.ai implementation begins after v1.0.0 through `IMPLEMENTATION_PLAN_PROVIDER_EXPANSION.md`.
