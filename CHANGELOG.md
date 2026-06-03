# CHANGELOG.md

All notable project changes are tracked here using SemVer-style versions.

## v0.4.2 — Hunyuan Image Upload Patch

**Status**: Current

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
