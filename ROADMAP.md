# ROADMAP.md — Versioned Product Roadmap

This roadmap is the source of truth for product direction. It separates what should be done before v1.0 from ideas that are valuable but should wait until the core personal workflow is stable.

## Product framing

This is a personal local Streamlit UI for hosted video and 3D generation, currently Replicate-powered, with fal.ai development intentionally deferred until v1.0.0 or later, not a production SaaS. The roadmap should prioritize:

- Avoiding invalid or wasteful paid provider calls.
- A clear, pleasant UI for the project owner and a non-technical household user.
- Useful history and output persistence.
- Honest cost/status messaging.
- Simple maintainable code and docs.

Do not add enterprise release process, CI/CD, auth, Docker, or heavy local inference stacks unless explicitly requested later.

---

## Current version estimate

**Current version: v0.3.1 — 3D Endpoint Compatibility Patch / Schema-Safe Beta**

Why v0.3.1:

- v0.1.0 represented the first working Streamlit + Replicate scaffold.
- v0.2.0 represented the post-review reliability/UX baseline: safer upload handling, Replicate output URL normalization, status polling, improved validation, cost display, and usable History filtering/links.
- v0.3.0 added model-specific schema constraints, schema-safe controls, pre-submit validation, clearer media roles, and generation-mode history for personal use.
- v0.3.1 fixes 3D model prediction creation for Replicate models that require the versioned prediction API and adds friendlier UI messaging for common Replicate/API failures.
- v0.4.0 is focused on Replicate-side improvements: the newer Hunyuan 3D 3.1 model and durable output/history improvements. fal.ai development starts at v1.0.0 or later, not in v0.x.
- This is still pre-1.0 because output/history persistence still relies on temporary Replicate URLs, live paid model QA is manual, and the UI still needs a plain-English polish pass for non-technical users.

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

2. **Provider-aware model catalogue**
   - Keep model selection workflow-first rather than provider-first.
   - Include the newer Replicate `tencent/hunyuan-3d-3.1` model in v0.4.0 with all current schema parameters exposed.

3. **Durable local output storage**
   - Preserve successful outputs after Replicate delivery URLs expire.
   - Store local file paths in History.
   - Make History useful as a permanent gallery, not just a temporary link table.

4. **Plain-English UX polish**
   - Explain model choices by outcome/use case, not only by model names.
   - Explain technical controls with tooltips and “leave this alone unless…” copy.
   - Make validation errors actionable for a non-technical user.

5. **Generation safety and dry-run visibility**
   - Show the request summary before paid generation.
   - Provide a non-paid dry-run payload preview for debugging.
   - Keep cost estimates honest: approximate or unknown is better than misleading precision.

6. **Minimal live smoke validation**
   - Run live paid tests only with explicit user authorization and expected cost/scope.
   - Before v1.0, verify at least one successful generation for each supported workflow:
     - text-to-video
     - image-to-video
     - image-to-3D

### Nice to have before v1.0 if time allows

These improve the experience but should not block v1.0 if the must-haves are complete:

- Rerun/remix from History.
- Favorites or simple notes in History.
- Better loading-stage copy and “taking longer than usual” messaging.
- A small model/schema diagnostics panel for development use.
- Basic prompt helper examples or starter prompts.

### Post-1.0 exploration

These are valuable but should wait until the core product is stable:

- Masking/inpainting workflows for models that support masks.
- Local mask creation or segmentation helper, possibly using a local model such as SAM/SAM2 or another lightweight background/object segmentation option.
- Batch generation.
- Side-by-side output comparison.
- fal.ai provider implementation and additional provider/catalog expansion.
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

**Status**: Implemented / current patch release

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
- Durable local output storage remains planned for v0.4.0.

---

## v0.4.0 — Hunyuan 3D 3.1 + Durable History

**Priority**: Highest next feature

**Status**: Planned

**Goal**: Add the newer Replicate Hunyuan 3D 3.1 model safely and make successful generations reusable after provider delivery URLs expire. fal.ai implementation is deferred until v1.0.0 or later.

### Hunyuan 3D 3.1 planned work

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

## v0.5.0 — Generation Safety, Dry-Run Payloads, and Schema Drift Checks

**Priority**: High before v1.0

**Status**: Planned

**Goal**: Make paid calls safer and make model/schema problems easy to diagnose without spending money.

### Planned work

- Add a “Preview request” or “Dry-run payload” expander before Generate:
  - model
  - generation mode
  - uploaded media roles
  - parameter values
  - estimated cost or “cost unknown”
- Add a copyable payload summary for debugging.
- Add a small non-paid schema/model diagnostics command or dev panel:
  - current latest version ID
  - whether versionless API is supported
  - local config inputs vs live schema inputs
  - unknown/missing fields
- Add optional Replicate live smoke commands gated by explicit environment variables:
  - `RUN_REPLICATE_SMOKE=1`
  - provider API token set in `.env`
- Add `RUN_FAL_SMOKE=1` only when v1.0.0+ fal.ai implementation begins.
- Use shortest/cheapest settings for smoke checks.
- Never run paid smoke checks by default.

### Acceptance criteria

- Default local checks run without network spending and without creating predictions.
- Paid smoke checks require explicit opt-in and a clear cost/scope note.
- Dry-run output is useful enough to debug model payload problems.
- Schema drift checks catch obvious local config vs live schema mismatches.

---

## v0.6.0 — Plain-English UX + Model Selection Polish

**Priority**: High before v1.0

**Status**: Planned

**Goal**: Make the app comfortable for a non-technical household user who wants to generate videos or 3D models without understanding model/API terminology.

### Planned work

- Replace bare model dropdown copy with model descriptions/cards or a richer selector:
  - best for
  - needs
  - output type
  - speed/cost expectation where known
  - recommended use case
- Add clear labels, help text, captions, or tooltips for model parameters:
  - Seed: “reuse this number to get a more repeatable result; leave random if unsure”
  - Duration: “how long the video should be”
  - Resolution: “image sharpness; higher is usually slower/more expensive”
  - Aspect ratio: “wide, square, or vertical framing”
  - Guidance scale: “how strongly the model follows the prompt”
  - Steps: “more steps can improve detail but take longer”
  - Pipeline/quality mode: “speed vs quality preset”
  - Texture size / mesh resolution / polygon budget: plain-English 3D quality trade-offs
- Add recommended-defaults copy for advanced settings.
- Keep technical/API parameter names out of the main UI when possible.
- Consider an explicit Simple / Advanced UI mode if the existing expander is not enough.
- Improve validation errors so they explain how to fix the issue.
- Add better empty states and upload guidance, especially for image-to-3D:
  - one clear centered subject
  - simple background
  - good lighting
  - avoid multiple objects or tiny/cropped subjects

### Acceptance criteria

- A non-technical user can understand the main controls without model jargon.
- Advanced controls explain when to change them and when to leave them alone.
- Model selection helps choose between Wan, Seedance, Hunyuan3D/Hunyuan 3D 3.1, and TRELLIS by desired outcome.
- Browser/manual QA checks UI copy for clarity, not just functional correctness.

---

## v0.7.0 — Better Errors, Progress, and Recovery

**Priority**: Medium before v1.0

**Status**: Planned

**Goal**: Turn technical failures and long waits into actionable user-facing messages.

### Planned work

- Translate common Replicate/API errors:
  - 401: token missing or invalid
  - 404: model endpoint/version mismatch or model ID problem
  - 422: invalid setting; identify the relevant control where possible
  - network/timeout: connection or Replicate availability issue
  - prediction failed: show model error and prediction URL
- Show prediction URL during generation, not only after completion/failure.
- Improve loading-stage copy:
  - uploading image
  - queued by Replicate
  - generating
  - finalizing output
- Add “this is taking longer than usual” copy after model-specific thresholds.
- Investigate cancel support only if Replicate exposes it cleanly and it is simple.

### Acceptance criteria

- Common errors are understandable without reading Python/HTTP exception details.
- The user always knows whether a job is waiting, running, done, or failed.
- Failed jobs preserve useful debugging information.

---

## v0.8.0 — History Reuse and Creative Iteration

**Priority**: Nice to have before v1.0; can move post-1.0 if needed

**Status**: Planned

**Goal**: Make iterative creative workflows faster once durable History exists.

### Planned work

- Add “use these settings again” from History.
- Add copy prompt / copy seed / copy settings actions.
- Add simple favorites.
- Add optional notes per generation.
- Add prompt examples or starter chips for common workflows.
- Consider lightweight presets:
  - video: fast draft / balanced / higher quality
  - 3D: fast preview / balanced / detailed model

### Acceptance criteria

- A good prior result can be reused without manually re-entering prompt/settings.
- History helps compare and continue creative experiments.
- The feature remains lightweight and local; no account/user system.

---

## v0.9.0 — Model Capability Metadata Hardening

**Priority**: Medium before v1.0 if time allows; otherwise first post-v1.0 cleanup

**Status**: Planned

**Goal**: Make model input/output roles explicit enough to support future expansion safely.

### Planned work

Add richer model metadata beyond simple `supports_text` / `supports_image` flags:

```python
capabilities = {
    "provider": "replicate",  # future providers such as fal.ai start at v1.0+
    "provider_model_id": "tencent/hunyuan-3d-3.1",
    "modes": ["text_to_video", "image_to_video", "text_to_3d", "image_to_3d"],
    "media_roles": ["start_frame", "subject_image", "reference_image"],
    "endpoint_mode": "versionless" | "versioned",
    "output_types": ["video", "glb", "preview_video"],
    "conditional_requirements": [],
    "mutually_exclusive": [],
}
```

Use this metadata to drive:

- UI labels.
- validation.
- History mode labels.
- future masking/reference-media support.
- dry-run payload display.

### Acceptance criteria

- Adding a model no longer requires guessing media roles from generic image/audio flags.
- Future reference-media and mask fields have an obvious metadata home.
- Local validation remains schema-safe before paid calls.

---

## v1.0.0 — Stable Personal Local Release

**Priority**: Release target

**Status**: Planned

### Release criteria

- Durable output storage and permanent History/gallery behavior are implemented or explicitly documented as out of scope.
- Plain-English UX pass is complete for main controls, advanced controls, model selection, and common errors.
- Dry-run payload preview or equivalent request summary is available before paid generation.
- All implemented models have verified schema constraints and endpoint mode handling.
- At least one user-authorized live successful smoke generation has been run for each supported workflow:
  - text-to-video
  - image-to-video
  - image-to-3D
- Browser visual QA is complete for Video, 3D, and History tabs.
- Lightweight local checks cover core utility, validation, pricing, history, output normalization, and endpoint-mode behavior.
- README, CHANGELOG, ROADMAP, DECISIONS, AGENTS, and implementation docs agree on scope, version, model IDs, storage behavior, and known limitations.

### fal.ai development begins at v1.0.0

No fal.ai implementation work is planned for v0.x. Starting at v1.0.0 or later, add fal.ai through the provider-adapter plan in `IMPLEMENTATION_PLAN_PROVIDER_EXPANSION.md`, not through direct branches in `app.py`.

The first documented fal.ai candidate remains NVIDIA Cosmos 3 Super Image to Video:

- fal.ai model page: `https://fal.ai/models/nvidia/cosmos-3-super/image-to-video`
- Endpoint URL: `https://fal.run/nvidia/cosmos-3-super/image-to-video`
- Model ID / endpoint ID: `nvidia/cosmos-3-super/image-to-video`
- Category: image-to-video
- Pricing: `$0.05` per second of generated video, rounded up. Agentic generation is billed for each candidate video generated.
- OpenAPI schema URL: `https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=nvidia/cosmos-3-super/image-to-video`
- Output schema: `video` object with downloadable URL plus returned `seed`.

Acceptance criteria before any paid fal.ai call:

- fal.ai credentials are optional and never block Replicate-only use.
- Cosmos appears as a fal.ai image-to-video candidate with all schema parameters exposed through plain-English labels/help.
- Cosmos cost estimate accounts for generated duration and warns that agentic generation can multiply candidate renders/spend.
- Prompt and start-frame image are required before a paid fal.ai request.
- Uploaded images are converted into a fal-accessible URL/request payload through a verified path.
- Paid fal.ai smoke checks require explicit user authorization and expected cost/scope.

---

# Post-1.0 roadmap

Post-1.0 work should expand creative power only after the core local app is dependable.

## v1.1 — Masking and Inpainting Exploration

**Priority**: High post-1.0 exploration

**Goal**: Explore mask-based workflows for models that support inpainting or region-specific edits.

### Ideas to evaluate

- Identify Replicate video/image/3D-adjacent models that accept mask inputs.
- Add model metadata for mask support:
  - required mask format
  - image dimensions/alignment requirements
  - whether mask is binary, grayscale, alpha, or model-specific
  - whether mask is combined with start/reference image roles
- Explore local mask creation helpers:
  - local segmentation model such as SAM/SAM2 or a lightweight background/object segmentation option
  - simple brush-based mask editor if feasible in Streamlit
  - background removal as a simpler first step
- Keep local mask tooling optional and lightweight; do not turn the project into a local inference stack unless the workflow proves useful.
- Consider storing masks alongside generation history for reproducibility.

### Open questions

- Which supported/future Replicate models actually accept masks with useful inpainting behavior?
- Is a local SAM/SAM2-style helper fast and simple enough on the target machine?
- Is Streamlit adequate for mask drawing/editing, or should mask creation be done by uploading external mask files first?
- Should mask generation be a separate utility tab or embedded only when a selected model supports masks?

### Acceptance criteria for moving from exploration to implementation

- At least one target model has verified mask input schema and useful output behavior.
- A non-paid dry-run can validate image+mask payload shape.
- Any local masking helper is optional, documented, and does not make normal generation harder.
- The UI explains masks in plain English: “paint the area you want the model to change.”

---

## v1.2 — Model Catalogue Expansion

**Priority**: Medium post-1.0

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

- Every new model has capability metadata, validation, pricing notes, endpoint-mode handling, and docs.
- No model is added based on marketing claims alone; implementation follows the exact schema for the deployed model ID.
- Cost and limitations are clear before users spend money.

---

## v1.3 — Comparison, Batch, and Export Tools

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

## v1.4 — Pricing Refresh Workflow

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
| v0.5.0 | Generation safety, dry-run payloads, schema drift checks | High | Must-have v1.0 |
| v0.6.0 | Plain-English UX + model selection polish | High | Must-have v1.0 |
| v0.7.0 | Better errors, progress, and recovery | Medium | Strong v1.0 candidate |
| v0.8.0 | History reuse and creative iteration | Medium | Nice-to-have v1.0 |
| v0.9.0 | Model capability metadata hardening | Medium | Prepares for v1.0+ provider work without implementing fal.ai |
| v1.0.0 | Stable personal local release | Release | Release target |
| v1.1 | Masking and inpainting exploration | High | Post-1.0 |
| v1.2 | Model catalogue expansion | Medium | Post-1.0 |
| v1.3 | Comparison, batch, and export tools | Medium/low | Post-1.0 |
| v1.4 | Pricing refresh workflow | Low | Post-1.0 |
