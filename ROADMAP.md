# ROADMAP.md — Versioned Product Roadmap

This document replaces the old rev/iter roadmap with standard semantic-version planning.

## Current Version Estimate

**Current version: v0.2.0 — Local Beta / Capability-Safe Baseline**

Why v0.2.0:
- v0.1.0 represents the first working Streamlit + Replicate scaffold.
- v0.2.0 represents the post-review reliability/UX baseline: safer upload handling,
  Replicate output URL normalization, status polling, improved validation, cost display,
  and usable History filtering/links.
- This is still pre-1.0 because not every supported model has been live-tested with paid
  Replicate calls, browser visual QA was not completed in an environment with Chrome,
  and output/history persistence still relies on temporary Replicate URLs.

## Versioning Policy

This project uses SemVer-style versioning while pre-1.0:

- **0.x minor bumps**: meaningful product capability changes or UX architecture changes.
- **0.x patch bumps**: bug fixes, docs corrections, small UI polish, pricing table updates.
- **1.0.0**: stable local product baseline after live model smoke tests, browser QA,
  durable output/history behavior, and documented model capability validation.

During 0.x development, breaking internal changes are allowed, but user-facing workflows
should still be documented in this roadmap and README.

---

## v0.2.0 — Current Baseline

**Status**: Current

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

### Known limitations

- No live paid generation smoke test has been run for all models.
- No completed browser visual QA in the current agent environment.
- History links expire when Replicate delivery URLs expire, usually after about 1 hour.
- Wan 2.7 T2V currently uses generic video controls that can expose invalid Replicate
  values, including duration `1`, resolution `480p`, and aspect ratio `adaptive`.
- Model capabilities are still manually encoded and not rich enough for all Seedance-style
  multimodal combinations.
- Advanced multi-file/reference-media controls are intentionally not fully exposed yet.

---

## v0.2.1 — Wan 2.7 T2V Validation Patch

**Status**: Implemented

**Priority**: Immediate (merged into v0.3.0 implementation)

**Goal**: Prevent known invalid Wan 2.7 T2V requests before any paid Replicate
prediction is created.

### Triggering issue

Browser/API debugging found that the app's generic video controls do not match the live
Replicate schema for `wan-video/wan-2.7-t2v`.

Confirmed live schema constraints:

- `duration`: minimum `2`, maximum `15`
- `resolution`: only `720p` or `1080p`
- `aspect_ratio`: only `16:9`, `9:16`, `1:1`, `4:3`, `3:4`

Current invalid UI values to remove or block for Wan 2.7 T2V:

- duration `1`
- resolution `480p`
- aspect ratio `adaptive`

### Planned work

- Add model-specific parameter constraints for Wan 2.7 T2V in `src/models_config.py` or
  an equivalent validation layer.
- Update `app.py` controls so Wan 2.7 T2V only offers schema-valid values:
  - duration slider starts at `2`
  - resolution options are `720p`, `1080p`
  - aspect ratio options include `3:4` and exclude `adaptive`
- Add pre-submit validation that blocks invalid Wan 2.7 T2V payloads before calling
  `replicate.predictions.create()`.
- Surface validation failures as friendly `st.error()` messages instead of Replicate
  422 errors.

### Acceptance criteria

- Wan 2.7 T2V cannot submit duration `1`, resolution `480p`, or aspect ratio `adaptive`.
- Valid default Wan 2.7 T2V settings remain unchanged: `5s`, `1080p`, `16:9`.
- Invalid payload tests run without network access or paid Replicate calls.
- Manual browser QA confirms the Wan 2.7 controls match the accepted schema.

---

## v0.3.0 — Model Capability Matrix + Schema-Driven UX

**Priority**: Highest

**Status**: Implemented

**Goal**: Prevent invalid paid generations and make model input roles obvious.

Key deliverables:
- `ParamConstraint` struct + `param_constraints` field on every `ModelConfig`
- All 5 models have live-schema-validated constraints for enums, ranges, and nullable
- App widgets (duration, resolution, aspect_ratio, pipeline_type, numeric params)
  now use per-model constraints instead of generic hardcoded options
- Pre-submit parameter validation in `src/validation.py` blocks invalid payloads
  before any Replicate API call
- Bricked old pipeline_type values: `512_fast` → `512`, `2048_quality` → `1536_cascade`
- Wan 2.5 I2V duration changed from slider to dropdown [5, 10] matching live schema

### Why this comes next

The biggest remaining product risk is model semantic drift. Replicate model schemas can
change, and models like Seedance have richer input semantics than simple `supports_image`
or `requires_image` flags. The app should know whether an image is a start frame, end
frame, reference image, mask, or unsupported input before the user spends money.

### Planned work

- Add structured capability metadata to each model config, for example:

```python
capabilities = {
    "modes": ["text_to_video", "image_to_video"],
    "image_roles": ["first_frame", "last_frame", "reference"],
    "audio_roles": ["generate_audio", "reference_audio"],
    "video_roles": ["reference_video"],
    "supports_masks": False,
    "conditional_requirements": [
        {"if": "last_frame_image", "requires": "image"},
    ],
    "mutually_exclusive": [
        ["reference_images", "image"],
        ["reference_images", "last_frame_image"],
    ],
}
```

- Replace generic image upload copy with role-specific controls:
  - Start frame
  - End frame
  - Reference image(s)
  - Reference video
  - Reference audio
  - Mask, only when confirmed supported by the exact Replicate schema
- Add validation before paid calls:
  - Model-specific parameter ranges/enums match the live Replicate schema.
  - Last-frame image requires a start-frame image.
  - Reference media cannot be combined with mutually-exclusive first/last-frame fields.
  - Resolution/aspect ratio warnings when ignored by image-driven modes.
- Store generation mode in history:
  - `text_to_video`
  - `image_to_video`
  - `image_to_3d`
  - future: `video_extend`, `video_edit`, `masked_edit`
- Add a schema verification script that records the exact Replicate input schemas used by
  the app.
- Add regression tests for model validation rules.

### Current capability notes to preserve

| Model | Current App Mode | Capability Notes |
|---|---|---|
| `wan-video/wan-2.7-t2v` | Text-to-video | Text prompt required. Image not supported in current app. |
| `wan-video/wan-2.5-i2v-fast` | Image-to-video | Image + prompt required. |
| `bytedance/seedance-2.0` | Text-to-video / image-to-video | Image is optional and can act as first-frame input. Future UI should expose last-frame and reference media only after exact schema verification. Mask support is not confirmed. |
| `tencent/hunyuan3d-2` | Image-to-3D | Treat as image-only for this Replicate deployment. |
| `fishwowater/trellis2` | Image-to-3D | Current implementation target. Do not confuse with older `firtoz/trellis`. |

### Acceptance criteria

- UI labels make input role clear; no generic ambiguous “image” field for multimodal models.
- Invalid combinations are blocked before creating a Replicate prediction.
- Tests cover the validation rules for every implemented model.
- Docs include a model capability matrix matching `src/models_config.py`.

---

## v0.4.0 — Durable Output Storage + Permanent History Preview

**Priority**: High

**Goal**: Make successful outputs persist after Replicate URLs expire.

### Planned work

- Add optional server-side output storage:

```text
outputs/
├── videos/
└── models_3d/
```

- Save generated outputs from Replicate delivery URLs after successful predictions.
- Preserve current no-autosave behavior as a configurable option if desired.
- Update History to reference local files for permanent re-viewing.
- Add video thumbnails/gallery previews.
- Add file cleanup from History UI.
- Add database migration:
  - Keep `replicate_url`.
  - Add `local_file_path`.
  - Add `thumbnail_path` where useful.

### Naming scheme

`{model_name}_{type}_{datetime}.{ext}`

Examples:
- `wan_2_7_t2v_video_20260603_143052.mp4`
- `hunyuan3d_2_threed_20260603_145512.glb`
- `trellis_2_threed_20260603_150423.glb`

### Acceptance criteria

- A successful generation remains previewable after the original Replicate URL expires.
- History clearly distinguishes temporary Replicate URLs from permanent local files.
- Failed downloads do not lose the original Replicate URL or history metadata.

---

## v0.5.0 — Automated Tests + Optional Live Replicate Smoke Tests

**Priority**: High

**Goal**: Make local development safe and make paid API testing explicit.

### Planned work

- Add unit tests for:
  - `output_to_url()`
  - `sanitize_parameters()`
  - model requirement/capability validation
  - cost calculation
  - history recording
- Add optional live smoke tests gated by environment variables:
  - `RUN_REPLICATE_SMOKE=1`
  - `REPLICATE_API_TOKEN=...`
- Use cheapest/shortest settings for live smoke tests.
- Never run paid tests by default.
- Add a dry-run payload validator that prints the Replicate input payload without creating
  a prediction.

### Acceptance criteria

- Default test suite runs without network and without spending money.
- Paid smoke tests require explicit opt-in.
- README documents the exact commands and expected cost envelope.

---

## v0.6.0 — Expand Model Catalogue

**Priority**: Medium

**Goal**: Add more models only after capability/schema handling and persistence are solid.

### Candidate video models

- Kling Video 3.0 — premium multi-shot/audio workflows.
- Runway Gen-4.5 — top visual fidelity if available/priced reasonably through Replicate.
- Grok Imagine Video — social-media style clips.
- Hailuo 2.3 — balanced cost/quality.
- Google Veo 3.1 — native audio if available through supported APIs.

### Candidate 3D models

- Tripo 2.5 — fast prototyping.
- Rodin — sharp geometry/characters.
- DreamGaussian — fast multi-view.
- Zero123++ — multi-view from single image.

### Acceptance criteria

- Every new model has capability metadata, validation tests, pricing, and docs.
- No model is added based on marketing claims alone; implementation follows the exact
  Replicate schema for the deployed model ID.

---

## v0.7.0 — Pricing Refresh Workflow

**Priority**: Low

**Goal**: Keep static pricing useful without adding runtime pricing dependencies.

### Planned work

- Add a quarterly/manual pricing refresh workflow:
  1. Fetch current hardware pricing from Replicate pricing docs or API if available.
  2. Fetch or verify hardware assignments per model.
  3. Update `src/pricing.py`.
  4. Log old price → new price for audit.
- Consider a cron job only if automation is reliable.

### Considerations

- Replicate may not expose all pricing through an API.
- Web scraping may be brittle.
- Manual refresh remains acceptable unless pricing changes frequently.

---

## v1.0.0 — Stable Local Release

**Priority**: Release target

### Release criteria

- All implemented models have verified capability metadata.
- At least one live successful smoke generation has been run for each supported workflow.
- Browser visual QA is complete for Video, 3D, and History tabs.
- Durable output/history behavior is implemented or explicitly documented as out of scope.
- Tests cover core utility, validation, pricing, and history behavior.
- README, DECISIONS, AGENTS, and ROADMAP agree on scope, version, model IDs, and storage behavior.

---

## Priority Summary

| Version | Theme | Priority | Depends On |
|---|---|---:|---|
| v0.2.1 | Wan 2.7 T2V validation patch | Immediate | v0.2.0 |
| v0.3.0 | Model capability matrix + schema-driven UX | Highest | v0.2.0 |
| v0.4.0 | Durable output storage + permanent History preview | High | v0.2.0 |
| v0.5.0 | Automated tests + optional live smoke tests | High | v0.3.0 |
| v0.6.0 | Expand model catalogue | Medium | v0.3.0, preferably v0.4.0 |
| v0.7.0 | Pricing refresh workflow | Low | None |
| v1.0.0 | Stable local release | Release | v0.3.0–v0.5.0, storage decision |
