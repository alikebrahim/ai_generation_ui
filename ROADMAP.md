# ROADMAP.md — Versioned Product Roadmap

This roadmap is the source of truth for product direction. It separates what should be done before v1.0 from ideas that are valuable but should wait until the core personal workflow is stable.

## Product framing

This is a personal local Streamlit UI for hosted video and 3D generation, currently Replicate-powered, with fal.ai development intentionally deferred until after the v1.0.0 Replicate-only baseline, not a production SaaS. The roadmap should prioritize:

- Avoiding invalid or wasteful paid provider calls.
- A clear, pleasant UI for the project owner and a non-technical household user.
- Useful history and output persistence.
- Honest cost/status messaging.
- Simple maintainable code and docs.

Do not add enterprise release process, CI/CD, auth, Docker, or heavy local inference stacks unless explicitly requested later.

---

## Current version estimate

**Current version: v0.5.10 — History Preview and Layout Hardening Complete**

Why v0.5.10:

- v0.1.0 represented the first working Streamlit + Replicate scaffold.
- v0.2.0 represented the post-review reliability/UX baseline: safer upload handling, Replicate output URL normalization, status polling, improved validation, cost display, and usable History filtering/links.
- v0.3.0 added model-specific schema constraints, schema-safe controls, pre-submit validation, clearer media roles, and generation-mode history for personal use.
- v0.3.1 fixed 3D model prediction creation for Replicate models that require the versioned prediction API and added friendlier UI messaging for common Replicate/API failures.
- v0.4.0 added Hunyuan 3D 3.1 plus local-output/history scaffolding.
- v0.4.1 fixed the durable-history persistence bug, tightened Hunyuan 3D 3.1 prompt/image validation, and improved local-file History UX.
- v0.4.2 fixed Hunyuan 3D 3.1 image uploads by sending explicit image MIME data URIs instead of extensionless provider file URLs.
- v0.5.0–v0.5.10 completed the UI stabilization series: shared shell styling, focused Video/3D generation panels, human-readable media-role metadata, gallery-first History, separate Gallery/Records redraw views, inline History previews, and docs alignment.
- This remains pre-1.0 because live paid model QA is manual and generation safety/dry-run tooling is the next planned milestone.

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
   - Add the planned v0.6.5 Replicate 3D/texture models only after their current schemas, endpoint modes, outputs, and pricing are verified.

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

6. **Minimal live smoke validation**
   - Run live paid tests only with explicit user authorization and expected cost/scope.
   - Before v1.0, verify at least one successful generation for each supported workflow:
     - text-to-video
     - image-to-video
     - image-to-3D
     - text-to-3D

### Nice to have before v1.0 if time allows

These improve the experience but should not block v1.0 if the must-haves are complete:

- Better loading-stage copy and “taking longer than usual” messaging.
- Small copy-only History actions such as copy prompt / copy seed / copy settings, if they are easy and do not delay v1.0 readiness.
- Basic prompt helper examples or starter prompts.

### Post-1.0 exploration

These are valuable but should wait until the core product is stable:

- Rerun/remix from History.
- Favorites or simple notes in History.
- fal.ai provider implementation and additional provider/catalog expansion, including Meshy.
- Masking/inpainting workflows for models that support masks.
- Local mask creation or segmentation helper, possibly using a local model such as SAM/SAM2 or another lightweight background/object segmentation option.
- Batch generation.
- Side-by-side output comparison.
- Advanced prompt builder/templates.
- CSV/JSON export.
- Per-model quirks database.

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

**Status**: Current

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

**Status**: Planned

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

**Status**: Planned

**Goal**: Add the next Replicate-hosted 3D/texture models using the v0.6 metadata and dry-run safeguards, without creating paid predictions during development.

### Planned model candidates

- `tencent/hunyuan3d-2mv`
- `adirik/text2tex`
- `adirik/texture`
- `hyper3d/rodin`

### Planned work

- For each candidate, fetch current authoritative facts from Replicate before implementation:
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

## v0.7.0 — Better Errors, Progress, and Recovery

**Priority**: Medium before v1.0

**Status**: Planned

**Goal**: Keep failure and long-wait behavior understandable while preserving the minimal UI direction.

### Planned work

- Translate common provider/API errors in provider adapters.
- Show provider job URL during generation when available.
- Improve progress state handling without verbose visible copy.
- Add “taking longer than usual” messaging after model-specific thresholds only if it proves useful.
- Investigate cancel support only if provider APIs expose it cleanly and simply.

### Acceptance criteria

- Common errors are understandable without reading Python/HTTP exception details.
- The generation panel always shows whether a job is waiting, running, done, or failed.
- Failed jobs preserve useful debugging information.

---

## v0.8.0 — v1.0 Readiness and Authorized Smoke QA

**Priority**: Final pre-v1.0 milestone

**Status**: Planned

**Goal**: Verify the Replicate-only personal baseline end to end before declaring v1.0 stable.

### Planned work

- Run visible browser QA for:
  - Video page;
  - 3D page;
  - History Gallery view;
  - History Records view;
  - validation errors and empty states.
- With explicit user authorization and expected cost/scope, run one successful live smoke generation for each supported workflow:
  - text-to-video;
  - image-to-video;
  - image-to-3D;
  - text-to-3D.
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
- Browser visual QA is complete for Video, 3D, History Gallery, and History Records views.
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

## v1.1 — History Reuse and Creative Iteration

**Priority**: High post-1.0 quality-of-life

**Goal**: Make iterative creative workflows faster once the stable Replicate-only baseline is complete.

### Planned work

- Add “use these settings again” from History.
- Add copy prompt / copy seed / copy settings actions if not already added before v1.0.
- Add simple favorites and optional notes.
- Consider lightweight presets such as fast draft / balanced / detailed only if they do not clutter the main flow.

### Acceptance criteria

- A good prior result can be reused without manually re-entering prompt/settings.
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
| v0.6.0 | Safety, metadata audit, dry-run, schema diagnostics | High | Next major milestone |
| v0.6.5 | Replicate 3D and texture model expansion | High | Add verified Replicate models |
| v0.7.0 | Better errors, progress, and recovery | Medium | Strong v1.0 candidate |
| v0.8.0 | v1.0 readiness and authorized smoke QA | Highest | Final pre-v1.0 milestone |
| v1.0.0 | Stable Replicate-only personal local release | Release | Release target |
| v1.1 | History reuse and creative iteration | High | Post-1.0 quality-of-life |
| v1.2 | fal.ai provider expansion and Meshy exploration | High | Post-1.0 provider expansion |
| v1.3 | Masking and inpainting exploration | Medium | Post-1.0 exploration |
| v1.4 | Model catalogue expansion | Medium | Post-1.0 |
| v1.5 | Comparison, batch, and export tools | Medium/low | Post-1.0 |
| v1.6 | Pricing refresh workflow | Low | Post-1.0 |
