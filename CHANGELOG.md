# CHANGELOG.md

All notable project changes are tracked here using SemVer-style versions.

## Unreleased — Planning / Docs

### Added

- Added `IMPLEMENTATION_PLAN_PROVIDER_EXPANSION.md`, a provider-aware implementation plan for eventual v1.0.0+ expansion from Replicate-only to Replicate + fal.ai.
- Kept v0.4.0 focused on Replicate-side work: the newer Replicate `tencent/hunyuan-3d-3.1` model and durable output/history improvements.
- Documented Hunyuan 3D 3.1 schema details, endpoint mode, validation requirements, and UI/History expectations.
- Documented NVIDIA Cosmos 3 Super fal.ai schema details, pricing, validation requirements, and agentic-generation cost warning as v1.0.0+ planning, not v0.x implementation work.

### Verified without paid prediction

- Fetched `tencent/hunyuan-3d-3.1` model metadata/schema from Replicate.
- Confirmed latest version ID: `a2838628b41a2e0ee2eb19b3ea98a40d75f8d7639bf5a1ddd37ea299bb334854`.
- Confirmed Replicate API page reports `usesVersionlessApi: true` for Hunyuan 3D 3.1.
- Fetched fal.ai Cosmos 3 Super `llms.txt` and OpenAPI schema for v1.0.0+ planning without creating a paid request.

---

## v0.3.1 — 3D Endpoint Compatibility Patch

**Status**: Current

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
