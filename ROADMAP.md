# ROADMAP.md — Versioned Product Roadmap

This roadmap is the source of truth for product direction. It separates what should be done before v1.0 from ideas that are valuable but should wait until the core personal workflow is stable.

## Product framing

This is a personal local Streamlit UI for hosted **video**, **3D**, and **audio** generation, currently Replicate-powered, with fal.ai development intentionally deferred until after the v1.0.0 Replicate-only baseline, not a production SaaS. The roadmap should prioritize:

- Avoiding invalid or wasteful paid provider calls.
- A clear, pleasant UI for the project owner and a non-technical household user.
- Useful history and output persistence.
- Honest cost/status messaging.
- Simple maintainable code and docs.

Do not add enterprise release process, CI/CD, auth, Docker, or heavy local inference stacks unless explicitly requested later.

---

## Current version estimate

**Current version: v0.8.0 — Replicate audio (music + speech): Audio tab, nine models, local `outputs/audio/`, History + dry-run**

**Catalogue today**: 11 video models, 7 3D/texture models, 9 audio models (3 music + 6 speech).

Version history (summary):

- v0.1.0 represented the first working Streamlit + Replicate scaffold.
- v0.2.0 represented the post-review reliability/UX baseline: safer upload handling, Replicate output URL normalization, status polling, improved validation, cost display, and usable History filtering/links.
- v0.3.0 added model-specific schema constraints, schema-safe controls, pre-submit validation, clearer media roles, and generation-mode history for personal use.
- v0.3.1 fixed 3D model prediction creation for Replicate models that require the versioned prediction API and added friendlier UI messaging for common Replicate/API failures.
- v0.4.0 added Hunyuan 3D 3.1 plus local-output/history scaffolding.
- v0.4.1 fixed the durable-history persistence bug, tightened Hunyuan 3D 3.1 prompt/image validation, and improved local-file History UX.
- v0.4.2 fixed Hunyuan 3D 3.1 image uploads by sending explicit image MIME data URIs instead of extensionless provider file URLs.
- v0.5.0–v0.5.10 completed the UI stabilization series: shared shell styling, focused Video/3D generation panels, human-readable media-role metadata, gallery-first History, separate Gallery/Records redraw views, inline History previews, and docs alignment.
- v0.6.0 added dry-run/request preview, shared payload builders, schema diagnostics, metadata audit fields, and opt-in paid smoke scripts.
- v0.6.5 added Hunyuan3D 2 Multiview, Text2Tex, Adirik Texture, and Rodin Gen-2 with mesh/multiview file upload UI.
- v0.6.6–0.6.11 completed rich creative param exposure for using model capabilities (advanced_param_groups, param_help + dynamic help, high_impact_params with ★ markers, widget slider support, per-model presets with Apply/Reset on the richest models, “♻️ Load settings” remix from History, safer multi-file reference uploads, 3D tab capability filter + consistent name-based selection for parity with Video, layout tweaks for action prominence); plus pre-0.7 polish items (better loading-stage “taking longer than usual” messaging with time estimates, History copy-only actions for prompt/seed/settings, basic prompt helper examples/starter prompts loadable in the form).
- **Next planned**: v0.9.0 — authorized smoke QA and browser pass (video, 3D, **music**, **speech**).
- This remains pre-1.0 because v0.9.0 smoke and plain-English UX polish for v1.0 are still pending.

### Pre-1.0 path at a glance

| Order | Milestone | What it delivers |
|-------|-----------|------------------|
| Done | **v0.6.11** | creative param exposure (groups/help/★/presets) + remix/multi-ref/3D parity + pre-0.7 polish (loading messages, History copies, prompt starters) |
| Done | **v0.6.10** | 11 video models + workflow-aware Video tab |
| Done | **v0.6.5** / **v0.6.0** | 7 3D/texture models, dry-run + diagnostics |
| Done | **v0.7.0** | Clearer errors, progress, recovery |
| Done | **v0.8.0** | Audio tab: 3 music + 6 speech models |
| Next | **v0.9.0** | Browser QA + authorized smoke (video, 3D, **music**, **speech**) |
| Release | **v1.0.0** | Replicate-only personal baseline declared stable |

**Post-1.0** (not v1.0 blockers): Aleph keyframes, fal.ai — see sections below. Multi-reference uploads were completed in v0.6.11 for metadata-marked multi-file params.

---

## Versioning policy

This project uses lightweight SemVer-style versioning while pre-1.0:

- **0.x patch bumps**: bug fixes, docs corrections, small UI polish, pricing updates.
- **0.x minor bumps**: meaningful product capability changes or UX architecture changes.
- **1.0.0**: comfortable personal baseline after persistent outputs/history, clear non-technical UX, dry-run/safety tooling, and at least one authorized live smoke generation for each supported workflow.

During 0.x development, breaking internal changes are allowed, but user-facing workflows should remain documented in this roadmap and README.

---

## Pre-1.0 priority tiers

### Must have before v1.0

These are required for the app to feel like a dependable personal tool:

1. **Provider + endpoint safety**
   - Avoid broken paid calls when a provider endpoint, model ID, or version mode is wrong.
   - Track the Replicate endpoint mode per model and keep metadata structured so a future provider can be added cleanly.
   - For Replicate, track whether a model uses `model=`/versionless prediction creation or `version=` prediction creation.
   - Surface endpoint/model errors in plain English.

2. **Provider-aware model catalogue and metadata audit**
   - Keep model selection workflow-first rather than provider-first.
   - Keep current Replicate model metadata accurate for endpoint mode, input schema, output schema, capability flags, media roles, defaults, and pricing.
   - Before adding any model, fetch current provider facts from the official model page/API docs rather than relying on memory or marketing summaries.
   - Include the newer Replicate `tencent/hunyuan-3d-3.1` model in v0.4.0 with all current schema parameters exposed.
   - Additional Replicate 3D/texture models require verified schemas before addition (v0.6.5 added four models; see `IMPLEMENTATION_VER-0.6.5.md`).

3. **Durable local output storage**
   - Preserve successful outputs after Replicate delivery URLs expire.
   - Store local file paths in History.
   - Make History useful as a permanent gallery, not just a temporary link table.

4. **Minimal, familiar UX polish**
   - Keep model names unchanged while making the surrounding UI easier to scan.
   - Use concise labels, tooltips, and short subtexts instead of long visible explanations.
   - Make validation and failure messages direct and actionable.
   - Keep generation progress/result display in one focused panel.

5. **Generation safety and dry-run visibility**
   - Keep paid generation deliberate and visibly tracked.
   - Provide non-paid request/payload inspection where useful for debugging.
   - Keep cost estimates honest: approximate or unknown is better than misleading precision.

6. **Minimal live smoke validation** (see v0.8.0)
   - Run live paid tests only with explicit user authorization and expected cost/scope.
   - Use `ALLOW_PAID_REPLICATE_SMOKE=1` and `scripts/paid_smoke.py` when authorized.
   - Before v1.0, verify at least one successful generation for each core workflow:
     - text-to-video
     - image-to-video
     - image-to-3D
     - text-to-3D
     - music generation (v0.9.0)
     - speech / TTS (v0.9.0)
   - Optionally extend smoke coverage to v0.6.5 workflows (multiview 3D, mesh texturing, Rodin).

### Nice to have before v1.0 if time allows

These improve the experience but should not block v1.0 if the must-haves are complete:

- Better loading-stage copy and “taking longer than usual” messaging. (completed in v0.6.11)
- Small copy-only History actions such as copy prompt / copy seed / copy settings. (completed in v0.6.11)
- Basic prompt helper examples or starter prompts. (completed in v0.6.11)

### Post-1.0 exploration

These are valuable but should wait until the core product is stable:

- Rerun/remix from History (basic version landed in 0.6.11; richer variants later).
- Favorites or simple notes in History.
- fal.ai provider implementation and additional provider/catalog expansion, including Meshy.
- Masking/inpainting workflows for models that support masks.
- Local mask creation or segmentation helper, possibly using a local model such as SAM/SAM2 or another lightweight background/object segmentation option.
- Batch generation.
- Side-by-side output comparison.
- Advanced prompt builder/templates.
- CSV/JSON export.
- Per-model quirks database.

**Bigger architectural / creative explorations (logged for post-1.0 per user request 2026):**

- Model-specific form renderers (or a small registry of form fragments) for the most complex workflows instead of one giant generic `render_generation_form`.
- Side-by-side generation (two models, same prompt/media) for direct comparison.
- Visual “param explorer” or interactive cost/time/quality simulator for high-variance params (e.g. steps, guidance, texture size, num viewpoints).
- Full dynamic forms driven from Replicate (or future provider) OpenAPI schemas, using the existing diagnostics tooling, while keeping curated `ModelConfig` as the source of friendly labels, safe defaults, groups, help text, and high-impact flags.

---

## v0.2.0 — Previous Baseline

**Status**: Superseded by v0.3.0

### Implemented

- Streamlit single-page app with Video, 3D, and History tabs.
- Replicate integration for 5 models:
  - `wan-video/wan-2.7-t2v`
  - `wan-video/wan-2.5-i2v-fast`
  - `bytedance/seedance-2.0`
  - `tencent/hunyuan3d-2`
  - `fishwowater/trellis2`
- Text-to-video, image-to-video, and image-to-3D workflows.
- Cost estimates before/after generation where pricing is known.
- SQLite history with metadata, parameters, cost, status, and temporary output URL.
- Replicate prediction polling with visible status/elapsed time.
- Replicate output normalization for URL strings, lists, dicts, and `FileOutput.url`.
- Safe serialization of uploaded files into history metadata.
- Basic model requirement flags: `requires_text`, `requires_image`.

### Known limitations carried forward

- History links expire when Replicate delivery URLs expire, usually after about 1 hour.
- No live paid generation smoke test has been run for every model/workflow.
- Browser visual QA is still manual.
- Model capabilities are manually encoded and need richer media-role metadata.
- Advanced multi-file/reference-media controls are intentionally not fully exposed yet.

---

## v0.3.0 — Model Constraints + Schema-Safe Controls

**Status**: Implemented

**Goal**: Prevent invalid paid generations and make implemented model inputs clearer.

### Implemented

- `ParamConstraint` struct + `param_constraints` field on every `ModelConfig`.
- Live-schema-validated constraints for enums, ranges, and nullable inputs.
- Per-model controls for duration, resolution, aspect ratio, pipeline type, and numeric advanced settings.
- Pre-submit parameter validation in `src/validation.py` before any Replicate prediction call.
- Safer media role labels such as “start frame image” and “subject image”.
- Generation mode stored in History:
  - `text_to_video`
  - `image_to_video`
  - `image_to_3d`
- Old invalid TRELLIS pipeline values replaced with current schema values.
- Wan 2.5 I2V duration changed to fixed choices `[5, 10]` matching the live schema.

### Current model capability notes

| Model | Current App Mode | Capability Notes |
|---|---|---|
| `wan-video/wan-2.7-t2v` | Text-to-video | Text prompt required. Image not supported in current app. |
| `wan-video/wan-2.5-i2v-fast` | Image-to-video | Image + prompt required. |
| `bytedance/seedance-2.0` | Text-to-video / image-to-video | Image is optional and can act as first-frame input. Future UI should expose last-frame/reference media only after exact schema verification. |
| `tencent/hunyuan3d-2` | Image-to-3D | Treat as image-only for this Replicate deployment. |
| `fishwowater/trellis2` | Image-to-3D | Current implementation target. Do not confuse with older `firtoz/trellis`. |

---

## v0.3.1 — 3D Endpoint Compatibility Patch

**Priority**: Immediate

**Status**: Implemented / superseded by v0.4.0

**Goal**: Fix 404 errors for Replicate 3D models that do not support the versionless model prediction endpoint.

### Triggering issue

Hunyuan3D 2.0 returned:

```text
Unexpected error: ReplicateError Details: status: 404 detail: The requested resource could not be found
```

Investigation found that `tencent/hunyuan3d-2` exists but its Replicate API page reports `usesVersionlessApi: false`. It must be called through a versioned prediction request.

### Implemented fix

- Resolve the current `latest_version.id` for 3D models.
- Call `replicate.predictions.create(version=version_id, input=input_params)` instead of `replicate.predictions.create(model=model_id, input=input_params)` for the 3D path.
- Cache the latest version lookup during the process.
- Verify with non-paid probes and local checks.

### Release notes

- Package/docs version is updated to v0.3.1.
- `CHANGELOG.md` records the endpoint compatibility fix and non-paid verification.
- Common Replicate/API errors now get friendlier UI messages.

### Follow-up for later milestones

- Run a paid live image-to-3D smoke test only with explicit user authorization and expected cost.
- Durable local output storage was implemented in v0.4.0 and patched in v0.4.1.

---

## v0.4.0 — Hunyuan 3D 3.1 + Durable History

**Priority**: Highest next feature

**Status**: Implemented / superseded by v0.4.1

**Goal**: Add the newer Replicate Hunyuan 3D 3.1 model safely and make successful generations reusable after provider delivery URLs expire. fal.ai implementation is deferred until after the v1.0.0 Replicate-only baseline.

### Implemented

#### Hunyuan 3D 3.1

- Added Replicate `tencent/hunyuan-3d-3.1` to model catalogue with all schema parameters exposed.
- Generation modes: `text_to_3d` and `image_to_3d` with mutual-exclusivity guard.
- Uses versionless Replicate API (`model=`) as required.

#### Durable local output storage

- New `download_output()` utility downloads provider URLs to `outputs/videos/` and `outputs/models_3d/`.
- All 6 generation functions download outputs locally after success.
- Database migration: `local_file_path`, `thumbnail_path`, `file_size_bytes` columns added.
- Original provider URL preserved even if local download fails.

#### History gallery UI

- Gallery card view with status badges, model/mode labels, timestamp, cost, and 💾/☁️ availability indicators.
- Table view moved to collapsible expander with an "Availability" column.
- Result displays show local file path when saved.

### Naming scheme

Add Replicate model `tencent/hunyuan-3d-3.1` as a v0.4.0 3D model.

Verified non-paid model/page facts gathered 2026-06-03:

- Replicate URL: `https://replicate.com/tencent/hunyuan-3d-3.1`
- Model ID: `tencent/hunyuan-3d-3.1`
- Description: “3D models with texture fidelity and geometry precision”
- Latest version ID: `a2838628b41a2e0ee2eb19b3ea98a40d75f8d7639bf5a1ddd37ea299bb334854`
- Replicate API page reports `usesVersionlessApi: true`, so this model should use the versionless path:
  - `replicate.predictions.create(model="tencent/hunyuan-3d-3.1", input=...)`
- Hardware shown by Replicate page/API metadata: `CPU`
- Pricing shown by Replicate page: `$0.16 per unit` / about 62 units for $10; page also shows p50 price around `$0.012`. Treat as pricing-to-verify before showing a confident estimate.
- Output schema: single URI string. Expect a downloadable 3D asset URL; normalize through the existing output URL normalization path.

Expose all current schema parameters:

| Parameter | Type | Default | Constraint | Plain-English label / guidance |
|---|---|---:|---|---|
| `prompt` | string, nullable | none | max 1024 chars; mutually exclusive with `image` | “Describe the 3D model” — use when generating from text instead of a subject image. |
| `image` | URI string, nullable | none | jpg/png/jpeg/webp; 128–5000 px per side; max 6 MB; mutually exclusive with `prompt` | “Subject image” — use one clear object, simple background, no text, object >50% of frame. |
| `enable_pbr` | boolean | `false` | ignored when `generate_type="Geometry"` | “Generate realistic materials” — adds PBR material/texture detail when using normal textured mode. |
| `face_count` | integer | `500000` | min `40000`, max `1500000` | “Model detail / polygon count” — higher can improve detail but may be slower/heavier. |
| `generate_type` | enum | `Normal` | `Normal` or `Geometry` | “Output style” — Normal generates a textured model; Geometry generates a white/untextured model. |

Validation requirements:

- Require exactly one of `prompt` or `image`.
- Reject prompt + image together before creating a paid prediction.
- Reject neither prompt nor image before creating a paid prediction.
- Enforce prompt max length, image file type/size guidance, face count range, and enum values locally.
- Show `enable_pbr` as disabled or explain it has no effect when `generate_type="Geometry"`.

History/UI requirements:

- Add generation modes for this model:
  - `text_to_3d`
  - `image_to_3d`
- Show it in the 3D tab as the more advanced Hunyuan option.
- Plain-English model card: “Newest Hunyuan 3D model; supports text or subject image; good for higher-fidelity geometry and texture.”
- Keep old `tencent/hunyuan3d-2` available until user decides to remove or de-emphasize it.

### Durable output/history planned work

- Add optional local output storage:

```text
outputs/
├── videos/
├── models_3d/
└── thumbnails/
```

- Download successful video/3D outputs from provider delivery URLs.
- Store both original provider output URL and local file path.
- Add database migration fields:
  - `local_file_path`
  - `thumbnail_path`
  - optional `file_size_bytes`
- Preserve the original provider output URL even if local download fails.
- Add a History gallery view with cards for recent generations.
- Make temporary vs permanent output status obvious.
- Add basic local cleanup/delete controls.

### Naming scheme

```text
{model_name}_{mode}_{datetime}.{ext}
```

Examples:

- `wan_2_7_t2v_text_to_video_20260603_143052.mp4`
- `hunyuan3d_2_image_to_3d_20260603_145512.glb`
- `hunyuan_3d_3_1_text_to_3d_20260603_150110.glb`
- `trellis_2_image_to_3d_20260603_150423.glb`

### Acceptance criteria

- Hunyuan 3D 3.1 appears in the 3D tab with prompt/image modes and all schema parameters exposed with plain-English labels/help.
- Hunyuan 3D 3.1 dry-run/payload path uses versionless Replicate model prediction mode, not the versioned path required by Hunyuan3D 2.0/TRELLIS.
- A successful generation remains previewable after the original provider URL expires.
- History clearly distinguishes local files from temporary provider URLs.
- Failed local downloads do not lose the original provider URL or history metadata.
- History stores endpoint/model metadata needed for current Replicate workflows and future provider expansion.
- The History tab is useful as a personal gallery, not just a table.

---

## v0.4.1 — Durable History Patch

**Priority**: Immediate patch

**Status**: Implemented / superseded by v0.4.2

**Goal**: Fix the v0.4.0 release-readiness blockers found in local review.

### Implemented

- SQLite History now persists `local_file_path`, `thumbnail_path`, and `file_size_bytes` for new generations.
- Hunyuan 3D 3.1 now requires exactly one input: text prompt or subject image.
- Hunyuan 3D 3.1 prompt length is validated locally against the 1024-character schema limit.
- Prompt + uploaded subject image is rejected before the app enters the generation status flow.
- History checks whether saved local paths still exist and distinguishes:
  - `💾 Local`
  - `⚠️ Missing local file`
  - `☁️ Temporary`
- Local file actions no longer rely on browser-blocked `file://` links; small/medium files use Streamlit download buttons and large files show the local path.
- Download filenames include a nanosecond suffix to avoid same-second overwrites.

### Verification

- Local compile and Ruff checks passed.
- Non-paid probes verified DB persistence, Hunyuan validation, and download filename collision resistance.
- No paid Replicate prediction was run.

---

## v0.4.2 — Hunyuan Image Upload Patch

**Priority**: Immediate patch

**Status**: Implemented / superseded by v0.4.9

**Goal**: Fix Hunyuan 3D 3.1 image-to-3D uploads where valid JPG files could reach the model as extensionless provider file URLs and be rejected as `Unsupported image format: .`.

### Implemented

- Hunyuan 3D 3.1 image inputs are converted to explicit `data:image/...;base64,...` URIs before the Replicate request.
- Local byte sniffing recognizes JPG/JPEG, PNG, and WEBP even when a file-like upload has no reliable filename.
- Hunyuan 3D 3.1 image uploads are checked against the model’s 6 MB image limit before a paid call.
- History records uploaded-image metadata instead of storing the base64 data URI.

### Verification

- Confirmed the reported JPG is valid `image/jpeg` locally.
- Non-paid probes verified real-file JPG conversion, nameless file-like JPG conversion, invalid-image rejection, Hunyuan request payload encoding, and History metadata safety.
- No paid Replicate prediction was run.

---

## v0.4.3–v0.4.9 — Architecture Stabilization Series

**Priority**: Completed prerequisite for v0.5.0

**Status**: Complete in v0.4.9

**Goal**: Sorted out structure while the app is still small enough to refactor comfortably. Keep v0.4.x Replicate-only in behavior, but separate UI, generation orchestration, provider execution, output storage, and History persistence so later work is easier and less fragile.

Detailed implementation guidance lives in `IMPLEMENTATION_PLAN_ARCHITECTURE_REFACTOR.md`; completion notes live in `IMPLEMENTATION_VER-0.4.3-TO-0.4.9.md`.

### Online research assessment

No online research is required for v0.4.3–v0.4.9. This is an internal refactor using established local patterns:

- Streamlit presentation modules.
- Service-layer orchestration.
- Provider adapter / ports-and-adapters boundary.
- Typed dataclasses for generation results and output assets.
- Repository-style SQLite history access.

Use online/provider docs only when a future task depends on current external facts, such as Replicate schema drift diagnostics, pricing refreshes, or post-v1.0 fal.ai implementation.

### v0.4.3 — UI Module Split

**Goal**: Turn `app.py` into a thin Streamlit shell and move tab/form/result rendering into `src/ui/`.

Completed work:

- Create `src/ui/` package.
- Move generic parameter form rendering to `src/ui/forms.py`.
- Move Video tab to `src/ui/video_tab.py`.
- Move 3D tab to `src/ui/threed_tab.py`.
- Move History tab to `src/ui/history_tab.py`.
- Move result rendering and `<model-viewer>` HTML helpers to `src/ui/result_views.py` / `src/ui/model_viewer.py`.
- Preserve current generation dispatch and behavior.

Acceptance criteria met:

- `app.py` mostly performs page setup and calls `render_video_tab()`, `render_3d_tab()`, and `render_history_tab()`.
- No generation behavior, provider behavior, or database schema changes.
- Compile and Ruff checks pass.

### v0.4.4 — Generation Registry + Domain Types

**Goal**: Remove hard-coded model dispatch from UI modules and introduce shared internal shapes for requests/results/assets.

Completed work:

- Create `src/domain.py` with lightweight dataclasses such as `OutputAsset`, `CostEstimate`, and `GenerationResult`.
- Create `src/generation_registry.py` mapping each model slug to its current generation handler.
- Replace UI `if model.name == ...` generation branches with `run_generation(model, params, progress_callback=...)`.
- Keep compatibility with existing result dicts while the full result model evolves.

Acceptance criteria met:

- UI modules no longer contain per-model generation `if/elif` chains.
- Every configured model has a handler.
- Local registry probe, compile, and Ruff checks pass.

### v0.4.5 — Provider-Aware Model Metadata

**Goal**: Make the current Replicate catalogue provider-aware without adding fal.ai behavior.

Completed work:

- Extend `ModelConfig` with `provider`, `provider_model_id`, and `provider_endpoint`.
- Set all current models to `provider="replicate"`.
- Move Replicate endpoint mode into model metadata:
  - versionless for current video models and Hunyuan 3D 3.1
  - versioned for Hunyuan3D 2.0 and TRELLIS 2
- Start moving media-role UI metadata into model config where obvious.
- Keep compatibility helpers for existing `replicate_id` usage if needed.

Acceptance criteria met:

- Endpoint mode is model data, not hidden generation-control flow.
- Current behavior remains Replicate-only and unchanged.
- Provider metadata probe, compile, and Ruff checks pass.

### v0.4.6 — Replicate Adapter Extraction

**Goal**: Isolate Replicate SDK details in one adapter.

Completed work:

- Create `src/providers/base.py` and `src/providers/replicate.py`.
- Move prediction creation, polling, latest-version lookup, output normalization, and Replicate-friendly errors into `ReplicateAdapter`.
- Store versioned/versionless endpoint mode in `ModelConfig.provider_endpoint`; wrappers use the adapter for creation/polling.
- Update video/3D wrappers to use the adapter instead of direct SDK calls.

Acceptance criteria met:

- Direct `replicate.predictions.create(...)` usage is isolated in the Replicate provider adapter.
- Direct provider SDK calls are no longer in generation wrappers.
- Non-paid branch probes, compile, and Ruff checks pass.

### v0.4.7 — Output Asset + Storage Service

**Goal**: Represent outputs as one or more assets and centralize local saving.

Completed work:

- Create `src/storage_service.py`.
- Normalize generated videos, 3D models, and preview videos as `OutputAsset` entries.
- Move local download, extension detection, MIME detection, and local filename generation into the storage service.
- Keep temporary compatibility keys such as `url`, `model_url`, and `video_url` until result views fully use assets.

Acceptance criteria met:

- Output handling no longer assumes exactly one URL per generation.
- TRELLIS model + preview video fit the same asset model.
- Local asset serialization/MIME probe, compile, and Ruff checks pass.

### v0.4.8 — Provider-Aware History Service

**Goal**: Make History provider-aware and less fragile before richer History or fal.ai work.

Completed work:

- Add provider-aware History fields:
  - `provider`
  - `provider_model_id`
  - `provider_job_id`
  - `provider_job_url`
  - `output_assets_json`
- Keep `replicate_url` for backward compatibility.
- Create `src/history_service.py` with typed history records while keeping `cost_tracker.py` backward-compatible.
- Keep the existing History UI tuple API stable while typed provider-aware queries are available through `HistoryService`.

Acceptance criteria met:

- Existing History rows remain readable.
- New rows can store provider/job/assets metadata.
- Fresh-schema and legacy-migration SQLite probes pass.
- Compile and Ruff checks pass.

### v0.4.9 — Integration Hardening + Dry-Run Foundation

**Goal**: Finish the architecture cleanup and leave the app ready for the v0.5 UI/UX pass plus later request preview/dry-run work.

Completed work:

- Introduce `src/generation_service.py` as the UI's generation entry point.
- Add a non-paid request-preparation hook that can return provider, model, mode, sanitized params, provider endpoint and sanitized payload summary without creating predictions.
- Remove obsolete duplicate helpers where safe.
- Re-run accumulated local probes.
- Align docs after the refactor series.

Acceptance criteria met:

- UI calls a generation service rather than provider/generation wrappers directly.
- A clean no-paid-call request-preparation hook exists for later safety/dry-run work.
- v0.4.x remains Replicate-only in behavior.
- Compile, Ruff, and accumulated non-paid probes pass.

---

## v0.5.0–v0.5.10 — Minimal UI/UX + Gallery History Series

**Priority**: Complete

**Status**: Complete

**Source of truth**: `UI_Decisions.md`

**Goal**: Make the local Streamlit app feel like a clean, familiar creative generation interface before adding more provider/model complexity. Keep model names unchanged, minimize visible explanatory copy, improve the tab/header presentation, make generation progress/results obvious, and turn History into a visual gallery with thumbnails/previews.

### Delivered design direction

- Minimal creative-tool feel, not an API dashboard.
- Keep model names as they are.
- Add minimal styling for a more pleasant `Video` / `3D` / `History` tab/header presentation.
- Use light containers/spacing where helpful; avoid heavy custom styling.
- Keep visible copy short; use tooltips/subtexts mostly for parameter help.
- Keep `Advanced controls` collapsed and simply labeled.
- Keep Generate after `Advanced controls`.
- Use focused inline generation panels, not modals, for v0.5.x.
- Result replaces loading state; no separate success banner required.
- Failed generations show failure/error details in the same panel.
- Completed result remains visible until the next generation replaces it.
- Use explicit mode selection for multi-mode models.
- Label media inputs by role: start frame, end frame, subject image, reference image.
- History becomes gallery-first with `Gallery` and `Records` as separate redraw views, not concurrently rendered internal tabs.
- Use ffmpeg for first-frame video thumbnails when available, with graceful fallback.
- 3D cards use static/provider previews when available; interactive viewer stays in result/detail view.
- Inline History previews stay on the History page through query-param-backed navigation.
- If a 3D prediction returns multiple useful assets, download/link all of them to the same generation/prediction.

### v0.5.0 — Minimal UI shell, layout reliability, and nicer tabs

**Status**: Done

**Goal**: Establish the v0.5 visual baseline and fix the layout issues found during visible-browser QA.

Delivered work:

- Fixed clipped Generate buttons and bottom spacing.
- Added minimal styling for a more pleasant `Video` / `3D` / `History` tab/header area.
- Added light form/section containers where useful.
- Kept visible copy minimal.
- Kept parameter explanations mostly in tooltips.
- Kept Generate after `Advanced controls`.

### v0.5.1 — Focused generation panel for Video

**Status**: Done

**Goal**: Make video generation progress and result display happen in one obvious place.

Delivered work:

- Added focused inline generation panel for video generation.
- Showed existing status / elapsed / prediction ID details while running.
- Replaced loading with the video result on completion.
- Showed failure message/details in the same panel.
- Removed redundant success banners/toasts where they added clutter.

### v0.5.2 — Focused generation panel for 3D

**Status**: Done

**Goal**: Give 3D generation the same focused progress/result behavior as Video.

Delivered work:

- Added focused inline generation panel for 3D generation.
- Showed existing status / elapsed / prediction ID details while running.
- Replaced loading with 3D result/open/download actions on completion.
- Showed failure message/details in the same panel.

### v0.5.3 — Hunyuan 3D 3.1 mode selector

**Status**: Done

**Goal**: Replace prompt/image mutual-exclusivity explanation with a clear input-mode choice.

Delivered work:

- Added `Create from text` / `Create from image` selector for Hunyuan 3D 3.1.
- Showed only the relevant input for the selected mode.
- Prevented invalid text+image or neither-input states before paid calls.

### v0.5.4 — Media role metadata and start/end frame pattern

**Status**: Done

**Goal**: Make media inputs role-aware and prepare for models with start/end frames.

Delivered work:

- Added model/config metadata for media roles.
- Rendered role-specific labels instead of generic `Upload Image`.
- Showed start frame as the visible upload when supported.
- Hid optional end frame behind an optional control when supported.
- Kept prompt visible for start/end-frame models.

### v0.5.5 — Video thumbnails for History cards

**Status**: Done

**Goal**: Make video History cards visually useful.

Delivered work:

- Added thumbnail extraction for video outputs when a first frame or preview asset is available.
- Displayed video thumbnails in History cards when local assets exist.
- Kept fallback previews available when a thumbnail could not be generated.

### v0.5.6 — 3D previews and multi-asset History

**Status**: Done

**Goal**: Capture all useful 3D outputs in History instead of only the primary asset.

Delivered work:

- Stored multiple 3D output assets when models return more than one useful file.
- Added static/provider preview handling for 3D assets where available.
- Preserved the interactive viewer for the result/detail panel.

### v0.5.7 — History Gallery/Records split and copy polish

**Status**: Done

**Goal**: Split the History experience into a gallery view and a records view.

Delivered work:

- Added `Gallery` and `Records` views inside History.
- Kept summary cards and filter controls available.
- Improved copy around local files, temporary links, and download actions.

### v0.5.8 — Gallery-first History layout and pagination prep

**Status**: Done

**Goal**: Make the gallery the primary History view while keeping records accessible.

Delivered work:

- Made gallery the default History view.
- Kept the records table available for troubleshooting and lookup.
- Preserved download/open actions and asset-awareness messaging.
- Kept the gallery usable with a larger generation set.

### v0.5.9 — Final UX hardening and docs alignment

**Status**: Done

**Goal**: Finish the v0.5 UI/UX pass and align docs before moving to safety/dry-run or later milestones.

Delivered work:

- Reviewed spacing, sections/components, tab styling, generation panels, and History cards across Video, 3D, and History.
- Updated README/CHANGELOG/ROADMAP/version docs to reflect v0.5.9 completion.
- Verified compile and Ruff checks locally.
- Kept browser QA out of this implementation pass, per request.

Acceptance criteria:

- Compile and Ruff checks pass.
- Docs agree on v0.5.x behavior and remaining known limitations.

### v0.5.10 — History preview/layout hardening

**Status**: Done

**Goal**: Apply the user-provided layout sketches and live-prediction feedback to make previews and History browsing behave reliably.

Delivered work:

- Replaced top-level tabs with query-param-backed segmented navigation for `Video`, `3D`, and `History`, so preview links can stay on History.
- Changed History `Gallery` / `Records` from concurrently rendered tabs to a segmented selector that redraws exactly one view body.
- Kept the History preview area inline and always visible when a gallery item is selected.
- Backfilled missing video thumbnails for existing local files when ffmpeg is available, then re-queried History so Gallery reflects the repaired metadata.
- Confirmed History recency ordering is newest first by timestamp and id.
- Added native Streamlit card actions for thumbnail preview, local downloads, and opening local files in the desktop file finder.

Acceptance criteria:

- `?page=history` opens History directly.
- Gallery and Records behave as separate redraw views.
- Existing local video generations with repairable thumbnails appear in Gallery.
- Completed generation previews do not require expanding a collapsed status widget.


---

## v0.6.0 — Safety, Metadata Audit, Dry-Run, and Schema Diagnostics

**Priority**: High before v1.0, after v0.5.x UI/UX baseline

**Status**: Complete

**Source of truth**: `IMPLEMENTATION_VER-0.6.0.md`

**Goal**: Use the v0.4.9 request-preparation hook and a current model-metadata audit to make paid calls safer and make model/schema problems easy to diagnose without spending money.

### Planned work

- Audit every implemented Replicate model against current provider facts before extending the catalogue:
  - model page URL and provider model ID;
  - endpoint mode (`model=` versionless vs `version=` latest-version path);
  - input schema, required/optional fields, ranges, enums, defaults, and nullable values;
  - output schema and whether the model can return multiple useful assets;
  - hardware/pricing source and date checked.
- Add optional “Preview request” / dry-run payload visibility where useful for debugging.
- Show a concise request summary and copyable technical payload in a collapsed/debug area.
- Add small non-paid schema/model diagnostics for current Replicate models.
- Add optional paid smoke commands only behind explicit environment variables and user authorization.

### Acceptance criteria

- Default local checks run without spending money and without creating predictions.
- Paid smoke checks require explicit opt-in and clear cost/scope.
- Dry-run output is useful enough to debug payload problems without cluttering the normal UI.
- Every current model has verified schema constraints, endpoint mode handling, output metadata, and pricing notes.

---

## v0.6.5 — Replicate 3D and Texture Model Expansion

**Priority**: High before v1.0, after v0.6 safety/metadata foundations

**Status**: Complete

**Source of truth**: `IMPLEMENTATION_VER-0.6.5.md`

**Goal**: Add the next Replicate-hosted 3D/texture models using the v0.6 metadata and dry-run safeguards, without creating paid predictions during development.

### Delivered (v0.6.5)

- `tencent/hunyuan3d-2mv` — multiview image-to-3D (`front_image` required)
- `adirik/text2tex` — `.obj` + prompt → textured mesh
- `adirik/texture` — mesh upload + prompt → textured output(s)
- `hyper3d/rodin` — text-to-3D with optional reference image mode
- Mesh/multiview file upload UI (`file_input_params` on `ModelConfig`)
- Payload builders, registry handlers, and dry-run support for all four models

### Original planned work (completed)

- For each candidate, fetched authoritative facts from Replicate before implementation:
  - `replicate.com` model page and model/API metadata;
  - current input schema and available parameters;
  - output schema and all useful downloadable assets;
  - endpoint mode/version requirements;
  - hardware and pricing/cost-estimation basis;
  - example payloads only when they match the current schema.
- Add the models to `src/models_config.py` with provider metadata, capability flags, media-role metadata, defaults, constraints, and pricing notes.
- Add generation wrapper/registry entries only after dry-run payloads can be inspected locally.
- Preserve output assets locally and store provider/job/output metadata in History.
- Keep model-specific UI copy plain-English and avoid exposing raw API names when friendly labels are available.

### Acceptance criteria

- Each added model has documented source URLs/date checked for schema and pricing.
- Local validation blocks missing/invalid inputs before any paid call.
- Dry-run/request preview shows the exact payload that would be sent.
- Compile, Ruff, model registry, metadata, and History/output probes pass.
- No paid Replicate prediction is created unless explicitly authorized with scope and expected cost.

---

## v0.6.10 — Video Model Expansion + Workflow-Aware UI

**Priority**: High before v1.0 (after v0.6.5, alongside or before v0.7.0)

**Status**: Complete (v0.6.10)

**Source of truth**: `IMPLEMENTATION_VER-0.6.10.md`

**Goal**: Add eight Replicate video models with verified schemas and reshape the Video tab so users can pick a **workflow** (text-to-video, image-to-video, motion transfer, video edit, multimodal) and see only the inputs that model supports — without turning the UI into an API dashboard.

**Prerequisite**: v0.6.0 dry-run/safety tooling and v0.6.5 file-upload patterns (extend uploads to **video** files for motion/edit models).

### Models to add (schema-checked 2026-06-04)

| Planned slug | Replicate ID | User-facing intent |
|--------------|--------------|-------------------|
| `happyhorse-1.0` | `alibaba/happyhorse-1.0` | Text-to-video or animate one image (3–15s) |
| `kling-v3-omni` | `kwaivgi/kling-v3-omni-video` | Multimodal generation (refs, start/end, quality tier) |
| `seedance-2.0-fast` | `bytedance/seedance-2.0-fast` | Faster Seedance-style multimodal (480p/720p) |
| `gen-4.5` | `runwayml/gen-4.5` | High-quality T2V/I2V (5s or 10s only) |
| `dreamactor-m2.0` | `bytedance/dreamactor-m2.0` | Character image + driving video → animation |
| `aleph-2` | `runwayml/aleph-2` | Edit an uploaded clip with a text instruction |
| `kling-v3-motion` | `kwaivgi/kling-v3-motion-control` | Transfer motion from reference video to character image |
| `kling-o1` | `kwaivgi/kling-o1` | Natural-language video modification (optional refs) |

**Already in catalogue (unchanged)**: `bytedance/seedance-2.0` — keep; `seedance-2.0-fast` is a separate faster variant.

Replicate pages: `https://replicate.com/<owner>/<model>` for each ID above.

### Why the UI must change

Current Video tab layout works for **prompt + optional single image** models. New models introduce distinct media roles:

| Capability | Models | UI impact |
|------------|--------|-----------|
| Driving / source **video** upload | Dreamactor, Kling motion, Aleph | New upload type; required fields |
| **Motion transfer** (image + video) | Dreamactor, Kling motion | Two labeled uploads; not “optional image” |
| **Video edit** (video + prompt) | Aleph, Kling O1 | Copy and layout say “edit”, not “generate” |
| **Multimodal references** (arrays) | Kling Omni, Kling O1, Seedance Fast | Sections for refs / start-end; array upload strategy |
| **Mode / tier** enums | Kling family | Plain labels in Advanced (“Quality tier”, etc.) |
| **Strict duration enums** | Gen-4.5 (5/10), Happyhorse (3–15) | Dropdowns, not generic sliders |

### Planned UI direction (summary)

Detailed wireframes and phase breakdown live in `IMPLEMENTATION_VER-0.6.10.md`.

1. **Workflow-first filter** (top of Video tab)
   User picks: *Make from text* | *Animate image* | *Motion from video* | *Edit video* | *All models*
   → Model dropdown lists only matching models (11+ total when “All” selected).

2. **`workflow_archetype` on `ModelConfig`**
   Drives which form layout renders: `text_or_image_video`, `multimodal_video`, `motion_transfer`, `video_edit`.

3. **Per-archetype form sections** (minimal creative-tool feel)
   - **Text/image**: mode radio like Hunyuan 3D 3.1 where needed.
   - **Multimodal**: prompt + start frame + optional end frame + collapsed “Reference media”.
   - **Motion transfer**: side-by-side or stacked **Character image** + **Driving video**.
   - **Video edit**: **Source video** + **Edit instructions** prompt; keyframes in Advanced (phase decision).

4. **Extend `file_input_params` to video** (`mp4`, `mov`, `webm`) — reuse v0.6.5 upload plumbing and dry-run previews.

5. **Keep** Preview request (no charge), validation, payload builders, and `model_diagnostics` probes per model.

6. **Phase** multi-file reference arrays (`reference_images`, `reference_videos`, `reference_audios`) — v0.6.10 can start with one reference; v0.6.11 completes metadata-marked multi-file upload controls.

### Suggested implementation phases

| Phase | Scope |
|-------|--------|
| 1 | Catalogue + Happyhorse + Gen-4.5 (familiar T2V/I2V patterns) |
| 2 | Dreamactor + Kling motion (video upload + motion layout) |
| 3 | Aleph + Kling O1 edit paths (single source video + prompt) |
| 4 | Seedance Fast + Kling Omni multimodal (array/reference UI) |
| 5 | Workflow filter + docs/version alignment |

### Acceptance criteria

- Each model: verified schema, endpoint mode, `media_roles`, constraints, pricing notes, dry-run payload.
- Workflow filter correctly narrows models; “All” still exposes full list.
- Motion/edit models show **required** video upload with plain-English labels.
- Invalid combinations blocked before paid calls; dry-run matches live payload builders.
- `uv run python scripts/model_diagnostics.py` passes without creating predictions.
- Paid smoke only with explicit authorization (`ALLOW_PAID_REPLICATE_SMOKE=1`).

### Resolved decisions (v0.6.10)

- Reference **arrays**: single-file MVP shipped in v0.6.10; multi-file upload controls completed in v0.6.11 for metadata-marked multi-file params.
- **Aleph keyframes**: **post-1.0**; v0.6.10 ships prompt + source video only.
- **Two-step** model picker: not required; workflow filter is enough for v1.0.
- **Seedance 2.0 vs 2.0 Fast**: both remain in catalogue (Fast capped at 720p).

---

## v0.7.0 — Better Errors, Progress, and Recovery

**Priority**: Medium before v1.0

**Status**: Complete (v0.7.0)

**Source of truth**: `IMPLEMENTATION_VER-0.7.0.md`

**Goal**: Keep failure and long-wait behavior understandable while preserving the minimal UI direction.

### Delivered

- Expanded `friendly_error_message` for common HTTP/provider failures, canceled jobs,
  content-policy blocks, and long raw traces; `technical_error_detail` for expanders.
- `ReplicateAdapter.wait_for_prediction` and `prediction_result_dict` for consistent
  polling and failure payloads across video and 3D.
- `src/generation_progress.py` and `src/ui/generation_panel.py` — plain-English status
  labels, long-wait hints (3 min video / 7 min 3D), Replicate job link during polling.
- Failed previews: link button + “Technical details” expander with raw provider message.
- Cancel UI deferred (Replicate supports cancel; Streamlit sync run blocks in-tab cancel).

### Acceptance criteria

- [x] Common errors are understandable without reading Python/HTTP exception details.
- [x] The generation panel always shows whether a job is waiting, running, done, or failed.
- [x] Failed jobs preserve useful debugging information.

---

## v0.8.0 — Replicate Audio Model Expansion (Music + Speech)

**Priority**: High before v1.0.0 (after v0.7.0)

**Status**: Complete (v0.8.0)

**Source of truth**: `IMPLEMENTATION_VER-0.8.0.md`

(Snapshot files: `IMPLEMENTATION_VER-0.9.0-replicate-api-snapshot.json`, `IMPLEMENTATION_VER-0.9.0-pricing-scrape.json` — names kept from original fetch.)

**Goal**: Add dedicated **music** and **speech** generation via Replicate, with an **Audio** section in the app, the same dry-run/validation/history patterns as video and 3D, and plain-English workflow filters (music vs speech).

**Not in scope for v0.8.0**: fal.ai audio; stem editing; replacing video models’ built-in “generate audio” toggles.

### Authoritative data on disk (fetch-first, no paid predictions)

Before implementing v0.9.0, use these repo-root JSON snapshots (same pattern as v0.6.10):

| File | Contents |
|------|----------|
| [`IMPLEMENTATION_VER-0.9.0-replicate-api-snapshot.json`](IMPLEMENTATION_VER-0.9.0-replicate-api-snapshot.json) | Latest version IDs, OpenAPI `Input`/`Output`, required fields, resolved params, endpoint hints |
| [`IMPLEMENTATION_VER-0.9.0-pricing-scrape.json`](IMPLEMENTATION_VER-0.9.0-pricing-scrape.json) | Replicate page `billingConfig` tiers, p50 median, hardware label |

**Fetch method**: `replicate.models.get()` + OpenAPI schema; Replicate HTML `billingConfig` from model pages (no predictions).

**Verified 2026-06-04**: **9 of 9** planned Replicate IDs exist (includes `inworld/realtime-tts-1.5-max`).

### Models to add (schema-checked 2026-06-04)

**Music (3)**

| Planned slug | Replicate ID |
|--------------|--------------|
| `music-2.5` | `minimax/music-2.5` |
| `stable-audio-2.5` | `stability-ai/stable-audio-2.5` |
| `lyria-2` | `google/lyria-2` |

**Speech / TTS (6)**

| Planned slug | Replicate ID |
|--------------|--------------|
| `realtime-tts-2` | `inworld/realtime-tts-2` |
| `realtime-tts-1.5-max` | `inworld/realtime-tts-1.5-max` |
| `speech-2.8-hd` | `minimax/speech-2.8-hd` |
| `speech-2.8-turbo` | `minimax/speech-2.8-turbo` |
| `chatterbox` | `resemble-ai/chatterbox` |
| `elevenlabs-v3` | `elevenlabs/v3` |

Note: `stability-ai/stable-audio-2.5` was listed twice in planning notes — one catalogue entry only.

### Planned UI direction

- New **Audio** nav segment (alongside Video, 3D, History).
- Workflow filter: *Make music* | *Generate speech* | *All audio models*.
- `st.audio()` preview + download; outputs under `outputs/audio/`; History `model_type` = `audio`.
- Reuse Preview request, payload builders, and `model_diagnostics` (no paid dev probes).

### Acceptance criteria

- All nine models verified (OpenAPI, pricing, endpoint mode) and documented in the JSON snapshots above.
- Audio tab ships with music/speech-appropriate forms (not one generic layout).
- Invalid requests blocked before paid calls; dry-run matches live payloads.
- v0.8.0 smoke plan includes at least one authorized **music** and one **speech** workflow.

### Milestone order before v1.0

`v0.7.0` → **`v0.8.0` (audio)** → `v0.9.0` (smoke + QA) → `v1.0.0`

---

## v0.9.0 — v1.0 Readiness and Authorized Smoke QA

**Priority**: Final pre-v1.0 milestone

**Status**: Planned

**Source of truth**: `IMPLEMENTATION_VER-0.9.0.md`

**Goal**: Verify the Replicate-only personal baseline end to end before declaring v1.0 stable.

### Planned work

- Run visible browser QA for:
  - Video page;
  - 3D page;
  - Audio page;
  - History Gallery view;
  - History Records view;
  - validation errors and empty states.
- With explicit user authorization and expected cost/scope, run one successful live smoke generation for each supported workflow:
  - text-to-video;
  - image-to-video;
  - image-to-3D;
  - text-to-3D;
  - **music generation** (v0.8.0 audio tab);
  - **speech / TTS** (v0.8.0 audio tab).
- After each authorized smoke, verify:
  - completed result preview remains visible;
  - local output is saved when possible;
  - Gallery card appears with thumbnail/preview or clear placeholder;
  - Records row stores provider/job/local/output metadata;
  - cost/status messaging is honest.
- Do final docs/version alignment for README, CHANGELOG, ROADMAP, DECISIONS, AGENTS, and implementation notes.

### Acceptance criteria

- Browser QA covers all current pages/views and major states.
- Authorized live smoke checks pass or blockers are documented honestly.
- Lightweight local checks pass without paid calls.
- Docs and code agree on current scope, supported workflows, known limitations, and post-1.0 provider expansion.

---

## v1.0.0 — Stable Personal Local Release

**Priority**: Release target

**Status**: Planned

### Release criteria

- Durable output storage and permanent History/gallery behavior are implemented or explicitly documented as out of scope.
- Minimal UI/UX pass is complete for page navigation, forms, generation panels, controls, History Gallery, and History Records.
- Dry-run payload preview or equivalent request summary is available where useful before paid generation/debugging.
- All implemented models have verified schema constraints and endpoint mode handling.
- At least one user-authorized live successful smoke generation has been run for each supported workflow:
  - text-to-video
  - image-to-video
  - image-to-3D
  - text-to-3D
  - music generation (v0.9.0)
  - speech / TTS (v0.9.0)
- Browser visual QA is complete for Video, 3D, **Audio**, History Gallery, and History Records views.
- Lightweight local checks cover core utility, validation, pricing, history, output normalization, and endpoint-mode behavior.
- README, CHANGELOG, ROADMAP, DECISIONS, AGENTS, and implementation docs agree on scope, version, model IDs, storage behavior, and known limitations.

### fal.ai development begins after v1.0.0

No fal.ai implementation work is planned for v0.x or for the v1.0.0 Replicate-only release target. After v1.0.0, add fal.ai through the provider-adapter plan in `IMPLEMENTATION_PLAN_PROVIDER_EXPANSION.md`, not through direct branches in `app.py`.

The first documented fal.ai candidates include NVIDIA Cosmos 3 Super Image to Video and Meshy:

- fal.ai model page: `https://fal.ai/models/nvidia/cosmos-3-super/image-to-video`
- Endpoint URL: `https://fal.run/nvidia/cosmos-3-super/image-to-video`
- Model ID / endpoint ID: `nvidia/cosmos-3-super/image-to-video`
- Category: image-to-video
- Pricing: `$0.05` per second of generated video, rounded up. Agentic generation is billed for each candidate video generated.
- OpenAPI schema URL: `https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=nvidia/cosmos-3-super/image-to-video`
- Output schema: `video` object with downloadable URL plus returned `seed`.

Meshy note:

- Meshy should be treated as post-1.0 fal.ai/provider-expansion work.
- Before implementation, fetch the current fal.ai/Meshy model pages, OpenAPI schemas, endpoint IDs, available parameters, output shapes, and pricing directly from fal.ai; do not rely on stale notes or provider marketing summaries.

Acceptance criteria before any paid fal.ai call:

- fal.ai credentials are optional and never block Replicate-only use.
- Cosmos and any Meshy model candidates appear only after their current fal.ai schema parameters and pricing have been verified and exposed through plain-English labels/help.
- Cosmos cost estimate accounts for generated duration and warns that agentic generation can multiply candidate renders/spend.
- Prompt and start-frame image are required before a paid fal.ai request.
- Uploaded images are converted into a fal-accessible URL/request payload through a verified path.
- Paid fal.ai smoke checks require explicit user authorization and expected cost/scope.

---

# Post-1.0 roadmap

Post-1.0 work should expand creative power only after the core Replicate-only local app is dependable.

## Post-1.0 — Advanced video inputs

**Priority**: Medium post-1.0 (Replicate-only; not part of v1.0.0 scope)

**Status**: Partly resolved in v0.6.11; Aleph keyframe UI remains planned

**v0.6.11 resolved**: multi-file upload controls now exist for multimodal reference arrays such as `reference_images`, `reference_videos`, `reference_audios`, plus Rodin `images`, where the model metadata marks those params as multi-file. Continue to rely on dry-run payload preview and local validation before paid calls.

### 1. Aleph 2.0 keyframe editor UI

**Model affected**: `runwayml/aleph-2` (`aleph-2`).

**Goal**: Expose optional `keyframe_images` + `keyframe_positions` (up to 5 pairs) in plain English:

- Upload keyframe stills; set position per image (`first`, `last`, or seconds)
- Enforce parallel array lengths and file/size limits from Replicate schema
- Keep simple “video + edit prompt” path as the default entry

**Acceptance criteria**:

- Keyframe path optional; simple edit path unchanged.
- Documented in README/CHANGELOG when complete.

**Source**: `IMPLEMENTATION_VER-0.6.10.md` (v0.6.10 completion notes).

---

## v1.1 — Favorites and Creative Iteration Notes

**Priority**: Medium post-1.0 quality-of-life

**Goal**: Add lightweight curation on top of the History remix/copy/preset work already completed in v0.6.11.

### Already completed before v1.0

- History remix: load prior scalar settings back into the matching tab.
- Copy prompt / copy seed / copy settings actions.
- Lightweight per-model presets such as fast draft / balanced / detailed.

### Planned work

- Add simple favorites and optional notes.
- Consider small comparison/continuation affordances only if they do not clutter the main flow.

### Acceptance criteria

- A good prior result can be marked and annotated without manual bookkeeping.
- History helps compare and continue creative experiments.
- The feature remains lightweight and local.

---

## v1.2 — fal.ai Provider Expansion and Meshy Exploration

**Priority**: High post-1.0 provider expansion

**Goal**: Add fal.ai through the provider-adapter architecture after the Replicate-only v1.0 baseline is stable.

### Candidate fal.ai work

- NVIDIA Cosmos 3 Super Image to Video as the first documented image-to-video candidate.
- Meshy as a post-1.0 3D/provider-expansion candidate once exact fal.ai schemas, pricing, and outputs are verified.

### Guardrails

- fal.ai credentials remain optional and never block Replicate-only use.
- Every fal.ai model must have current model-page/OpenAPI schema, endpoint ID, available parameters, output shape, pricing, and cost multipliers verified before implementation.
- fal.ai models are added through provider adapters and shared model metadata, not direct UI branches.
- Paid fal.ai smoke checks require explicit user authorization and expected cost/scope.

---

## v1.3 — Masking and Inpainting Exploration

**Priority**: Medium post-1.0 exploration

**Goal**: Explore mask-based workflows for models that support inpainting or region-specific edits.

### Ideas to evaluate

- Identify Replicate/fal.ai video, image, and 3D-adjacent models that accept mask inputs.
- Add model metadata for mask support:
  - required mask format;
  - image dimensions/alignment requirements;
  - whether mask is binary, grayscale, alpha, or model-specific;
  - whether mask is combined with start/reference image roles.
- Explore local mask creation helpers:
  - local segmentation model such as SAM/SAM2 or a lightweight background/object segmentation option;
  - simple brush-based mask editor if feasible in Streamlit;
  - background removal as a simpler first step.
- Keep local mask tooling optional and lightweight; do not turn the project into a local inference stack unless the workflow proves useful.
- Consider storing masks alongside generation history for reproducibility.

### Open questions

- Which supported/future provider models actually accept masks with useful inpainting behavior?
- Is a local SAM/SAM2-style helper fast and simple enough on the target machine?
- Is Streamlit adequate for mask drawing/editing, or should mask creation be done by uploading external mask files first?
- Should mask generation be a separate utility page or embedded only when a selected model supports masks?

### Acceptance criteria for moving from exploration to implementation

- At least one target model has verified mask input schema and useful output behavior.
- A non-paid dry-run can validate image+mask payload shape.
- Any local masking helper is optional, documented, and does not make normal generation harder.
- The UI explains masks in plain English: “paint the area you want the model to change.”

---

## v1.4 — Model Catalogue Expansion

**Priority**: Medium post-1.0

**Goal**: Add more models only after capability/schema handling and persistence are solid.

### Candidate video models

- Kling Video 3.0 — premium multi-shot/audio workflows.
- Runway Gen-4.5 — top visual fidelity if available/priced reasonably through supported providers.
- Grok Imagine Video — social-media style clips.
- Hailuo 2.3 — balanced cost/quality.
- Google Veo 3.1 — native audio if available through supported APIs.

### Candidate 3D models

- Tripo 2.5 — fast prototyping.
- Additional Rodin variants only after the v0.6.5 `hyper3d/rodin` implementation is verified.
- DreamGaussian — fast multi-view.
- Zero123++ — multi-view from single image.

### Acceptance criteria

- Every new model has capability metadata, validation, pricing notes, endpoint-mode handling, and docs.
- No model is added based on marketing claims alone; implementation follows the exact schema for the deployed model ID.
- Cost and limitations are clear before users spend money.

---

## v1.5 — Comparison, Batch, and Export Tools

**Priority**: Medium/low post-1.0

**Goal**: Support heavier creative workflows without cluttering the simple default UI.

### Candidate features

- Side-by-side comparison from History.
- Batch generation with explicit total-cost confirmation.
- Prompt/settings templates.
- CSV/JSON export for generation metadata.
- Per-model quirks/notes database.

### Guardrails

- Keep batch generation opt-in with clear total expected cost.
- Keep comparison/export tools out of the simple generation path.
- Do not add multi-user/account concepts.

---

## v1.6 — Pricing Refresh Workflow

**Priority**: Low post-1.0

**Goal**: Keep static pricing useful without adding brittle runtime dependencies.

### Planned work

- Add a manual pricing refresh workflow:
  1. Fetch current hardware pricing from Replicate pricing docs or API if available.
  2. Fetch or verify hardware assignments per model.
  3. Update `src/pricing.py`.
  4. Log old price → new price for audit.
- Consider automation only if a reliable API is available.

### Considerations

- Replicate may not expose all pricing through an API.
- Web scraping may be brittle.
- Manual refresh remains acceptable unless pricing changes frequently.

---

## Priority summary

| Milestone | Theme | Priority | Target |
|---|---|---:|---|
| v0.3.1 | 3D endpoint compatibility patch | Immediate | Pre-1.0 patch |
| v0.4.0 | Hunyuan 3D 3.1 + durable History | Highest | Must-have v1.0 |
| v0.4.1 | Durable History patch | Immediate | Superseded by v0.4.2 |
| v0.4.2 | Hunyuan image upload patch | Immediate | Superseded by v0.4.9 |
| v0.4.3 | UI module split | Done | Architecture stabilization |
| v0.4.4 | Generation registry + domain types | Done | Architecture stabilization |
| v0.4.5 | Provider-aware model metadata | Done | Architecture stabilization |
| v0.4.6 | Replicate adapter extraction | Done | Architecture stabilization |
| v0.4.7 | Output asset + storage service | Done | Architecture stabilization |
| v0.4.8 | Provider-aware History service | Done | Architecture stabilization |
| v0.4.9 | Integration hardening + dry-run foundation | Superseded | Prepares safety and UI work |
| v0.5.0-v0.5.10 | Minimal UI/UX + gallery History series | Complete | UI stabilization milestone |
| v0.6.0 | Safety, metadata audit, dry-run, schema diagnostics | Complete | Done in v0.6.0 |
| v0.6.5 | Replicate 3D and texture model expansion | Complete | Done in v0.6.5 |
| v0.6.10 | Video model expansion + workflow-aware UI | Complete | Done in v0.6.10 |
| v0.7.0 | Better errors, progress, and recovery | Medium | Complete |
| v0.8.0 | Replicate audio (music + speech) | High | Complete |
| v0.9.0 | v1.0 readiness and authorized smoke QA | Highest | Next; final pre-v1.0 gate |
| v1.0.0 | Stable Replicate-only personal local release | Release | Release target |
| v1.1 | History reuse and creative iteration | High | Post-1.0 quality-of-life |
| v1.2 | fal.ai provider expansion and Meshy exploration | High | Post-1.0 provider expansion |
| v1.3 | Masking and inpainting exploration | Medium | Post-1.0 exploration |
| v1.4 | Model catalogue expansion | Medium | Post-1.0 |
| v1.5 | Comparison, batch, and export tools | Medium/low | Post-1.0 |
| v1.6 | Pricing refresh workflow | Low | Post-1.0 |
