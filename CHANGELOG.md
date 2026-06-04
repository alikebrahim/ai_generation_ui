# CHANGELOG.md

All notable project changes are tracked here using SemVer-style versions.

## v0.5.10 — History Preview and Layout Hardening

**Status**: Current

### Changed

- Replaced top-level Streamlit tabs with query-param-backed segmented page navigation so History preview links stay on the History page instead of resetting to Video.
- Changed History Gallery / Records from concurrently rendered internal tabs to a segmented selector that redraws the page as one view or the other.
- Kept History Gallery as the default visual view while Records remains available for troubleshooting and lookup.

### Fixed

- Fixed the post-generation preview experience so completed results stay in an always-visible inline preview/result panel instead of requiring the user to expand a collapsed status area.
- Fixed existing local video rows not showing in Gallery by backfilling missing thumbnails from local output files where ffmpeg is available, then re-querying History.
- Confirmed Gallery recency uses `ORDER BY timestamp DESC, id DESC` from `get_all_generations()`.
- Added native Streamlit card actions for thumbnail preview, local download, and opening local outputs in the file finder.

### Verification

- Ran `python -m compileall -q app.py src`.
- Ran `uv run ruff check .`.
- Browser QA confirmed `?page=history` opens History directly and Gallery/Records render as separate views.
- No paid Replicate prediction was created.

---

## v0.5.9 — UI/UX Baseline and Gallery History Complete

**Status**: Superseded by v0.5.10

### Added

- Added shared shell styling for the top-level Streamlit app and cleaner tab/header spacing.
- Reworked the Video tab into a focused generation/result panel with clearer labels and lighter copy.
- Reworked the 3D tab into a focused generation/result panel with clearer upload/help text and result presentation.
- Added human-readable media-role metadata and Hunyuan 3D 3.1 mode metadata in the model catalogue.
- Added gallery-first History rendering with richer local-file awareness, thumbnails/previews, and a split between gallery and records views.
- Added a new implementation/version note for the v0.5.0–v0.5.10 UI pass.

### Fixed

- Improved early validation handling so invalid inputs return from the tab renderer instead of leaving a broken generation flow active.
- Fixed layout reliability issues around spacing, visible controls, and panel composition.
- Tightened the History experience so local and temporary assets are shown more honestly.
- Replaced collapsible generation status widgets with an always-visible inline loading/result area, so the panel shows progress until the preview appears.
- Fixed duplicate History filter widgets that could crash Streamlit when both Gallery and Records tabs were rendered.
- Made video thumbnail creation reusable and backfilled thumbnails for existing local video history rows when ffmpeg is available.

### Verification

- Ran `python -m compileall -q app.py src`.
- Ran `uv run ruff check .`.
- Ran Streamlit AppTest render against the existing local history database.
- No paid Replicate prediction was created.

---

## v0.4.9 — Architecture Stabilization Complete

**Status**: Superseded by v0.5.10

### Added

- Split the Streamlit app into `src/ui/` modules for forms, Video tab, 3D tab, History tab, and result rendering.
- Added a generation registry and `UnifiedGenerationService` so UI tabs call a single service boundary instead of model wrappers directly.
- Added provider-aware model metadata (`provider`, `provider_model_id`, `provider_endpoint`) for all configured Replicate models.
- Added a Replicate provider adapter that isolates direct Replicate SDK calls.
- Added canonical output asset/storage service scaffolding and routed local output downloads through `StorageService`.
- Added provider-aware History support with provider model ID, provider job ID/URL, and output asset metadata columns while keeping the old `cost_tracker` API compatible.
- Added a non-paid `prepare_generation_request()` hook for v0.5 dry-run/request-preview work.
- Added `IMPLEMENTATION_PLAN_ARCHITECTURE_REFACTOR.md` and `IMPLEMENTATION_VER-0.4.3-TO-0.4.9.md` documenting the completed architecture series.

### Fixed

- Fixed legacy SQLite migration order so existing v0.4.2 databases can add provider columns before provider indexes are created.
- Removed duplicate History writes by keeping concrete generation wrappers as the single History write owner through v0.4.9.
- Kept `cost_tracker.get_all_generations()` tuple shape stable for the current History UI while exposing provider-aware typed queries through `HistoryService`.
- Unified domain output asset references around the canonical `src.output_asset.OutputAsset`.

### Verification

- Ran `python -m compileall -q app.py src`.
- Ran `uv run ruff check .`.
- Ran import probes for `src.history_service` and `src.generation_service`.
- Ran fresh-schema and legacy-schema SQLite migration probes.
- Ran registry/provider metadata and dry-run request-preparation probes.
- No paid Replicate prediction was created.

---

## v0.4.2 — Hunyuan Image Upload Patch

**Status**: Superseded by v0.4.9

### Fixed

- Fixed Hunyuan 3D 3.1 image-to-3D uploads where a valid JPG could be rejected by the model as `Unsupported image format: .`.
- Hunyuan 3D 3.1 now converts uploaded/local images to explicit `data:image/...;base64,...` URIs before the Replicate request, avoiding extensionless Replicate file URLs.
- Added local image byte sniffing for JPG/JPEG, PNG, and WEBP so nameless file-like uploads still preserve the correct MIME type.
- Kept History safe from base64 bloat by recording uploaded-image metadata instead of the data URI.
- Added local size validation for Hunyuan 3D 3.1’s 6 MB image limit before a paid call.

### Verification

- Confirmed the reported file `/home/alikebrahim/Downloads/edff8245-7a37-4580-9e86-bde0a8b71094.jpg` is a valid `image/jpeg`.
- Ran local non-paid probes for real JPG files, nameless file-like JPG uploads, invalid image rejection, Hunyuan request payload encoding, and History metadata safety.
- No paid Replicate prediction was created.

---

## v0.4.1 — Durable History Patch

**Status**: Superseded by v0.4.2

### Fixed

- Fixed `record_generation()` so `local_file_path`, `thumbnail_path`, and `file_size_bytes` are actually persisted to SQLite History rows.
- Added exact-one validation for Hunyuan 3D 3.1 prompt/image input so neither-input and both-input cases are blocked before paid Replicate calls.
- Enforced Hunyuan 3D 3.1 prompt length validation against the 1024-character schema limit.
- Moved uploaded-image validation into the pre-generation validation path so prompt + uploaded image errors are shown before the “Generating…” status flow.
- Replaced unreliable `file://` History links with local path display and Streamlit `download_button` controls for local files.
- History now distinguishes existing local files, missing local files, and temporary provider links.
- Made downloaded output filenames collision-resistant by adding a nanosecond suffix and parsing URL extensions without query-string tokens.
- Removed the unused duplicate downloader module so there is one download implementation.

### Verification

- Ran local non-paid probes for SQLite local-field persistence, Hunyuan 3D 3.1 validation, and download filename collision behavior.
- Ran local compile and Ruff checks.
- No paid Replicate prediction was created.

---

## v0.4.0 — Hunyuan 3D 3.1 + Durable History

**Status**: Superseded by v0.4.1

### Added

#### Hunyuan 3D 3.1 model

- Added Replicate `tencent/hunyuan-3d-3.1` as a v0.4.0 3D model supporting both text-to-3D and image-to-3D modes.
- New generation modes tracked in History: `text_to_3d` and `image_to_3d`.
- Uses versionless Replicate API (`model=`) as required by this model.
- Mutual-exclusivity guard: rejects prompt + image together before a paid call.
- Full schema parameters exposed: prompt, image, enable_pbr, face_count, generate_type.
- Pricing entries for hunyuan-3d-3.1 (CPU hardware).

#### Durable local output storage

- New `download_output()` utility in `src/utils.py` that downloads provider output URLs to local storage with automatic extension detection from URL paths and Content-Type headers.
- All 6 generation functions (3 video + 3 3D) now download outputs locally after successful generation:
  - `generate_wan_2_7_t2v` — downloads to `outputs/videos/`
  - `generate_wan_2_5_i2v` — downloads to `outputs/videos/`
  - `generate_seedance_2_0` — downloads to `outputs/videos/`
  - `generate_hunyuan3d_2` — downloads to `outputs/models_3d/`
  - `generate_hunyuan_3d_3_1` — downloads to `outputs/models_3d/`
  - `generate_trellis_2` — downloads model to `outputs/models_3d/` and preview video to `outputs/videos/` as thumbnail.
- New database columns: `local_file_path`, `thumbnail_path`, `file_size_bytes`.
- Schema migration in `init_db()` applies ALTER TABLE for all three columns if missing.
- `get_all_generations()` now returns the three new columns.
- Original provider URL is always preserved even if local download fails.

#### History gallery UI

- Gallery card view in the History tab showing status badges, model name, mode, timestamp, cost, and local/temporary availability icons.
- "💾 Saved locally" / "☁️ Temporary link" indicators per generation.
- Table view moved to a collapsible expander with a new "Availability" column.
- Generation result displays (video and 3D) now show local file path caption when saved, falling back to the original expiry caveat.
- `local_file_path` and `file_size_bytes` returned in result dicts from all 6 generation functions for UI display.

### Known limitations

- No paid live generation has been run for this release.
- Local file cleanup/delete controls are not yet implemented.
- No thumbnail preview generation — TRELLIS 2 preview video is stored as a convenience copy, not a true thumbnail.
- The naming scheme uses a generic `{prefix}-{timestamp}.{ext}` format rather than the model-specific naming planned in the roadmap.

---

## v0.3.1 — 3D Endpoint Compatibility Patch

**Status**: Superseded by v0.4.0

### Changed

- 3D generation now resolves each model's current Replicate `latest_version.id` and creates predictions with the versioned API path.
- Hunyuan3D 2.0 and TRELLIS 2 no longer rely on Replicate's versionless model prediction endpoint.
- App-level Replicate/API errors now get friendlier messages for common 401, 404, 422, and network/timeout failures.

### Fixed

- Replaced deprecated Streamlit `use_container_width=True` usage with `width="stretch"`.
- Verified `friendly_error_message` imports from `src.utils` in the local uv environment after the v0.3.1 error-message change.
- Fixed Hunyuan3D 2.0 404 failures caused by calling `replicate.predictions.create(model=...)` for a model that reports `usesVersionlessApi: false`.
- Reduced raw `ReplicateError` leakage in the Streamlit UI for common endpoint/schema/token issues.

### Verification

- Verified `tencent/hunyuan3d-2` and `fishwowater/trellis2` latest version IDs through Replicate's model API without creating paid predictions.
- Ran a non-paid probe confirming 3D predictions use `version=` rather than `model=`.
- Ran local compile and Ruff checks.

### Known limitations

- No paid live generation was run for this patch.
- Output URLs still expire after about 1 hour unless the user downloads them.
- Durable local output storage remains planned for v0.4.0.

---

## v0.3.0 — Schema-Safe Controls / Personal Local Beta

**Status**: Superseded by v0.3.1

### Added

- Per-model `param_constraints` for live-schema ranges, enums, and nullable values.
- Schema-driven controls for duration, resolution, aspect ratio, pipeline type, and generic enum parameters.
- Pre-submit parameter validation before Replicate prediction creation in both the UI flow and generation wrappers.
- Generation mode metadata in History (`text_to_video`, `image_to_video`, `image_to_3d`).
- Clearer media labels for Seedance start-frame input and image-to-3D subject images.

### Changed

- Wan 2.7 T2V controls now exclude invalid duration/resolution/aspect-ratio values.
- Wan 2.5 I2V duration is a dropdown with only `5` and `10` seconds.
- TRELLIS 2 pipeline options now match the live schema: `512`, `1024`, `1024_cascade`, `1536_cascade`.
- Seedance intelligent duration (`-1`) is treated as unknown-cost mode instead of a negative duration.
- History prompt search now treats search text literally instead of as a regex.

### Fixed

- Prevented Seedance auto-duration from producing negative cost totals.
- Prevented enum-only parameters such as Hunyuan3D octree resolution from rendering as free numeric inputs.
- Aligned package/docs version metadata around v0.3.0.

### Known limitations

- This remains a personal local beta, not a production release.
- Output URLs still expire after about 1 hour unless the user downloads them.
- Live paid model QA is manual and intentionally not part of a formal test suite.
- Durable local output storage is planned for a later milestone.

---

## v0.2.0 — Local Beta / Capability-Safe Baseline

**Status**: Superseded by v0.3.0

### Added

- Replicate prediction polling with visible status and elapsed-time UI.
- Replicate output normalization for URL strings, lists, dicts, and `FileOutput.url`.
- Safe uploaded-file metadata serialization for History records.
- Separate model requirement flags: `requires_text` and `requires_image`.
- Cost estimate labels before generation where pricing is known.
- Uploaded image preview and metadata display.
- History filtering by model and prompt search.
- Temporary output links in History with expiry caveat.
- Versioned roadmap with v0.3.0–v1.0.0 milestones.

### Changed

- Seedance 2.0 image input is treated as optional, enabling text-only generation.
- Wan I2V and 3D models still enforce required image inputs before paid calls.
- Video and 3D wrappers now use explicit polling instead of blocking waits.
- Docs now describe current Image-to-3D scope and `src/` source layout.
- ROADMAP now uses standard versioning rather than rev/iter language.

### Fixed

- Prevented raw Streamlit uploaded files from breaking JSON history serialization.
- Prevented uploaded file objects from failing 3D generation metadata handling.
- Avoided losing successful outputs due to Replicate `FileOutput` display/storage mismatch.
- Corrected stale docs references to `lib/` and stale TRELLIS model identifiers.

### Known limitations

- No live paid smoke generation has been run for every supported model.
- Browser visual QA is not complete in the current agent environment.
- Output URLs still expire after about 1 hour unless the user downloads them.
- Model capability semantics are not yet fully schema-driven.

---

## v0.1.0 — Initial Working Scaffold

### Added

- Initial Streamlit app with Video, 3D, and History tabs.
- Initial Replicate model wrappers for Wan, Seedance, Hunyuan3D, and TRELLIS.
- SQLite generation history and static pricing estimates.
- `.env`-based Replicate token loading.
- Project documentation, decisions, and first implementation plan.
