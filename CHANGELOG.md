# CHANGELOG.md

All notable project changes are tracked here using SemVer-style versions.

## v0.2.0 — Local Beta / Capability-Safe Baseline

**Status**: Current

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
