# v1.0.0+ Multi-Provider Expansion Plan — Replicate + fal.ai

> **For Hermes:** This plan is for post-v1.0 work. Do not implement fal.ai work in v0.x or in the v1.0.0 Replicate-only release target. Use the subagent-driven-development skill if implementing this plan task-by-task once post-v1.0 provider work begins.

**Prerequisite:** Complete or intentionally supersede the v0.4.3–v0.4.9 architecture stabilization plan in `IMPLEMENTATION_PLAN_ARCHITECTURE_REFACTOR.md` before starting real fal.ai implementation. The v0.4.x series should leave behind UI modules, provider-aware model metadata, a Replicate adapter, normalized output assets, provider-aware History, and a dry-run/request-preparation service hook.

**Goal:** Starting at v1.0.0 or later, expand the app from a Replicate-only local generator into a two-provider video/3D generation UI that supports Replicate and fal.ai without making the user think in API-specific terms.

**Architecture:** Introduce a thin provider layer underneath the existing Streamlit tabs. The UI should select workflows and models using common concepts, while provider adapters translate validated common inputs into Replicate or fal.ai payloads. History, cost/status messaging, output normalization, and dry-run previews should store provider metadata explicitly so each provider's quirks stay visible to developers but mostly hidden from non-technical users.

**Tech Stack:** Streamlit, Python 3.11+, uv, python-dotenv, Replicate Python client, fal.ai client or HTTP API once post-v1.0 implementation begins, SQLite history.

---

## Product direction

This is not a general marketplace for every generation API. This expansion starts at v1.0.0 or later; v0.x remains Replicate-only. The first expansion is specifically:

- Keep Replicate as the existing provider.
- Add fal.ai as a second provider.
- Support only models that fit the current product scope:
  - text-to-video
  - image-to-video, starting fal.ai with NVIDIA Cosmos 3 Super Image to Video
  - image-to-3D
- Keep image generation and local inference out of scope unless separately requested.
- Standalone music/speech via Replicate shipped in **v0.8.0**; see `IMPLEMENTATION_VER-0.8.0.md`. fal.ai audio remains post-v1.0.
- Video-to-video transformations remain a future consideration.

The user-facing mental model should be:

1. Choose what you want to make: Video or 3D.
2. Choose a model/use case card.
3. The app shows which provider powers it only as secondary context.
4. The app explains cost, speed, required inputs, and expected output in plain English.

Provider names matter for trust, pricing, debugging, and account setup, but they should not dominate the creative workflow.

---

## Design principles

1. **Provider-agnostic UI, provider-aware details**
   - Main labels should say what a model does, not which SDK it uses.
   - Secondary captions can show “Provider: Replicate” or “Provider: fal.ai”.
   - Errors, History, dry-run payloads, and diagnostics must include provider details.

2. **One model catalogue, multiple provider adapters**
   - `src/models_config.py` should remain the user-facing model catalogue.
   - Each model should include a provider field and provider-specific endpoint metadata.
   - Replicate/fal.ai quirks should live in adapters, not scattered through `app.py`.

3. **Common result shape**
   - Every provider should return the same internal generation result shape:
     - status
     - provider
     - model ID/name
     - generation mode
     - prediction/job/request ID when available
     - provider URL/dashboard URL when available
     - output URLs/files
     - raw metrics when available
     - estimated/actual cost when available
     - user-friendly error text

4. **Cost honesty over false precision**
   - Replicate cost can remain based on hardware/time estimates where available.
   - fal.ai pricing may be per request, per second, per megapixel, per model, or unavailable depending on endpoint.
   - If exact pricing is not known, show “cost unknown” or “estimate unavailable” rather than inventing a number.

5. **No paid calls without explicit user action**
   - Dry-run payload previews and provider diagnostics should be non-paid by default.
   - Live paid tests for either provider require explicit authorization and expected cost/scope.

---

## Proposed architecture

### Provider enum / identifiers

Add a stable provider identifier used everywhere internally:

```python
ProviderName = Literal["replicate", "fal"]
```

User-facing labels:

```python
PROVIDER_LABELS = {
    "replicate": "Replicate",
    "fal": "fal.ai",
}
```

### Model configuration shape

Extend model config with provider metadata:

```python
@dataclass(frozen=True)
class ModelConfig:
    key: str
    display_name: str
    provider: str  # "replicate" | "fal"
    provider_model_id: str
    model_type: str  # "video" | "3d"
    modes: list[str]
    media_roles: list[str]
    output_types: list[str]
    param_constraints: dict[str, ParamConstraint]
    provider_endpoint: dict[str, Any] = field(default_factory=dict)
```

Replicate example:

```python
ModelConfig(
    key="hunyuan3d_2_replicate",
    display_name="Hunyuan3D 2.0",
    provider="replicate",
    provider_model_id="tencent/hunyuan3d-2",
    provider_endpoint={"prediction_mode": "versioned"},
    ...
)
```

fal.ai model example, verified as the intended first fal.ai candidate:

```python
ModelConfig(
    key="nvidia_cosmos_3_super_i2v_fal",
    display_name="NVIDIA Cosmos 3 Super Image to Video",
    provider="fal",
    provider_model_id="nvidia/cosmos-3-super/image-to-video",
    provider_endpoint={
        "endpoint_url": "https://fal.run/nvidia/cosmos-3-super/image-to-video",
        "api_style": "fal_client.subscribe_or_http_queue",
        "docs_url": "https://fal.ai/models/nvidia/cosmos-3-super/image-to-video",
        "openapi_url": "https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=nvidia/cosmos-3-super/image-to-video",
    },
    ...
)
```

Do not add additional real fal.ai model IDs until their current schema, output format, and pricing are verified.

### Provider adapter interface

Create a provider abstraction instead of adding `if provider == ...` blocks throughout the app:

```python
class ProviderAdapter(Protocol):
    provider: str

    def validate_credentials(self) -> ProviderCredentialStatus: ...
    def build_payload(self, model: ModelConfig, params: dict[str, Any]) -> dict[str, Any]: ...
    def preview_request(self, model: ModelConfig, params: dict[str, Any]) -> DryRunRequest: ...
    def create_prediction(self, model: ModelConfig, payload: dict[str, Any]) -> ProviderJob: ...
    def poll_prediction(self, job: ProviderJob) -> ProviderJob: ...
    def normalize_output(self, job: ProviderJob) -> list[OutputAsset]: ...
    def estimate_cost(self, model: ModelConfig, params: dict[str, Any]) -> CostEstimate: ...
    def friendly_error(self, error: Exception | str) -> str: ...
```

Suggested files:

```text
src/providers/
├── __init__.py
├── base.py          # common dataclasses/protocols
├── replicate.py     # existing Replicate behavior moved here
└── fal.py           # fal.ai behavior added here
```

Keep existing `src/video_gen.py` and `src/threed_gen.py` as thin workflow wrappers at first, or replace them with a single provider-driven generation service once the adapter layer is stable.

### Common history fields

Add provider fields before or alongside provider implementation:

```sql
provider TEXT NOT NULL DEFAULT 'replicate'
provider_model_id TEXT
provider_job_id TEXT
provider_job_url TEXT
provider_status TEXT
output_assets_json TEXT
cost_source TEXT  -- estimated, actual, unavailable
```

History should still keep the current `model_name`, `model_type`, prompt, params, status, and replicate URL fields for compatibility until a migration fully normalizes outputs.

### Credential configuration

Use `.env` for both providers:

```bash
REPLICATE_API_TOKEN=
FAL_KEY=
```

Do not require both tokens to run the app. If one provider token is missing:

- Hide or disable that provider's models with a clear setup caption.
- Keep the other provider usable.
- In diagnostics, show “configured / missing” without revealing token values.

---

## UI/UX plan

### Model selection

Move from a plain model dropdown toward model cards or grouped labels:

```text
Video
  Fast text-to-video draft          Wan 2.7 T2V       Provider: Replicate
  Cinematic image-to-video          Seedance 2.0      Provider: Replicate
  Higher-fidelity first-frame video NVIDIA Cosmos 3 Super I2V Provider: fal.ai

3D
  Detailed model from subject image Hunyuan3D 2.0     Provider: Replicate
  Newer text-or-image 3D model      Hunyuan 3D 3.1    Provider: Replicate
  PBR textured object               TRELLIS 2         Provider: Replicate
  [future fal.ai 3D model label]    ...              Provider: fal.ai
```

Primary selection criteria should be outcome/use case:

- “Fast draft”
- “Higher detail”
- “Good for product/object images”
- “Good for character/reference image”
- “Budget-friendly”
- “Provider/account required”

### Provider filter

Add a lightweight provider filter only if model count makes it useful:

```text
Provider: All | Replicate | fal.ai
```

Default should be “All available models,” not “choose provider first.”

### Setup messaging

When credentials are missing:

```text
fal.ai models are hidden because FAL_KEY is not set in .env.
Add FAL_KEY=... and restart Streamlit to enable them.
```

or for disabled cards:

```text
Requires fal.ai API key. Add FAL_KEY to .env to use this model.
```

### Dry-run / request preview

For each provider, show a plain-English summary first, then technical payload in an expander:

```text
You are about to generate:
- Type: image-to-video
- Model: NVIDIA Cosmos 3 Super Image to Video
- Provider: fal.ai
- Needs: prompt + start frame image URL/upload
- Estimated cost: $0.05 per generated video second, rounded up; agentic generation can multiply cost by rendering candidate videos
```

Technical expander:

```json
{
  "provider": "fal",
  "endpoint": "fal-ai/...",
  "payload": {...}
}
```

### Errors

Errors should include:

- Plain-English summary.
- Provider-specific setup/action.
- Provider job URL if available.

Examples:

```text
fal.ai could not authenticate this request. Check FAL_KEY in .env.
```

```text
Replicate could not find this model endpoint/version. The model may require a versioned prediction call or its ID changed.
```

```text
fal.ai rejected one setting for this model. Try the recommended/default values, then use Preview request to inspect the payload.
```

### History

History cards/table should include Provider as a visible column/filter:

```text
Provider | Model | Workflow | Prompt | Cost | Output | Created
```

Filters:

- Workflow: Video / 3D / mode
- Provider: All / Replicate / fal.ai
- Status: success / failed / cancelled

History should keep provider job links separate from output links.

---

## Functional implementation tasks

### Task 1: Document provider model

**Objective:** Make docs agree that the project remains Replicate-only in v0.x and moves from Replicate-only to Replicate + fal.ai starting at v1.0.0 or later.

**Files:**
- Modify: `README.md`
- Modify: `ROADMAP.md`
- Modify: `DECISIONS.md`
- Modify: `REFERENCE.md`
- Modify: `AGENTS.md`

**Verification:** Read docs and confirm they no longer say “Replicate only” except when describing current implemented behavior.

### Task 2: Add provider metadata without changing behavior

**Objective:** Extend internal model config to record provider while keeping all current models on Replicate.

**Files:**
- Modify: `src/models_config.py`
- Modify: any code that constructs or displays model names

**Verification:** Existing local checks pass and all current models still render in the UI.

### Task 3: Add provider-aware history migration

**Objective:** Add provider fields to History with existing rows defaulting to Replicate.

**Files:**
- Modify: `src/cost_tracker.py`

**Verification:** A local probe can initialize a fresh DB and open an existing DB without losing rows.

### Task 4: Create provider adapter base types

**Objective:** Define the common result/job/output/cost shapes.

**Files:**
- Create: `src/providers/base.py`
- Create: `src/providers/__init__.py`

**Verification:** Import checks pass; no provider behavior changes yet.

### Task 5: Move Replicate behavior into adapter

**Objective:** Keep current Replicate generation behavior but route it through `ReplicateAdapter`.

**Files:**
- Create: `src/providers/replicate.py`
- Modify: `src/video_gen.py`
- Modify: `src/threed_gen.py`
- Modify: `src/utils.py` if output normalization moves

**Verification:** Non-paid payload probes and compile/lint checks pass. Do not run paid predictions without authorization.

### Task 6: Add fal.ai credential detection (post-v1.0)

**Objective:** Let the app know whether fal.ai can be used without requiring the token for Replicate-only use.

**Files:**
- Modify: `src/config.py`
- Modify: `.env.example` only when fal.ai implementation is actually being added

**Verification:** App starts with only `REPLICATE_API_TOKEN`, only `FAL_KEY`, both, or neither; unavailable providers are shown/hidden clearly.

### Task 7: Add NVIDIA Cosmos 3 Super as the first fal.ai model (post-v1.0)

> Meshy is also a post-v1.0 fal.ai/provider-expansion candidate, but it must get its own model-page/OpenAPI/pricing verification pass before implementation.

**Objective:** Add `nvidia/cosmos-3-super/image-to-video` as the first fal.ai pilot model rather than adding many unverified endpoints.

**Files:**
- Modify: `src/models_config.py`
- Create/modify: `src/providers/fal.py`
- Modify: `src/pricing.py` or add provider-aware pricing shape

**Verified non-paid facts:**
- fal.ai model page: `https://fal.ai/models/nvidia/cosmos-3-super/image-to-video`
- Endpoint URL: `https://fal.run/nvidia/cosmos-3-super/image-to-video`
- Model ID / endpoint ID: `nvidia/cosmos-3-super/image-to-video`
- Category: `image-to-video`
- Description: Cosmos3 is a collection of omnimodal world models for dynamic, high-quality video/image/audio/action-command generation from multimodal inputs.
- Pricing: `$0.05` per second of generated video, rounded up. Agentic generation is billed for each candidate video generated.
- OpenAPI schema URL: `https://fal.ai/api/openapi/queue/openapi.json?endpoint_id=nvidia/cosmos-3-super/image-to-video`
- Python usage uses `fal_client.subscribe("nvidia/cosmos-3-super/image-to-video", arguments={...})`.
- HTTP usage posts to `https://fal.run/nvidia/cosmos-3-super/image-to-video` with `Authorization: Key $FAL_KEY`.
- Output shape: `{ "video": { "url": "...mp4", "content_type": "video/mp4", ... }, "seed": <int> }`.

**Expose all current input parameters:**

| Parameter | Type/default | Constraint / UX guidance |
|---|---|---|
| `prompt` | required string | 1–4096 chars. Plain label: “Describe the motion and scene”. |
| `image_url` | required string URL | Conditioning first-frame image. In UI, use upload/start-frame image and convert to a fal-accessible URL before request. |
| `negative_prompt` | optional string, long NVIDIA default | Max 2048 chars in OpenAPI. Keep collapsed/advanced; empty string disables. |
| `enable_prompt_expansion` | bool, default `true` | Plain label: “Let Cosmos improve the prompt”. Uses a reasoner to rewrite the prompt; falls back to raw prompt if expansion fails. |
| `enable_agentic_generation` | bool, default `false` | Advanced/costly. Iteratively generates and critiques candidate videos; substantially slower and more expensive. |
| `agentic_max_iterations` | int, default `2` | Range `1`–`3`; only relevant when agentic generation is enabled. |
| `agentic_samples_per_iteration` | int, default `2` | Range `1`–`3`; multiplies candidate video renders and cost. |
| `agentic_early_stop` | bool, default `true` | Stop the agentic loop early when quality threshold is met. |
| `image_size` | object or enum, default `{width: 832, height: 480}` | Supports object `{width,height}` or enums `square_hd`, `square`, `portrait_4_3`, `portrait_16_9`, `landscape_4_3`, `landscape_16_9`; request is clamped/snapped to NVIDIA tiers/aspect ratios. |
| `num_frames` | int, default `189` | Range `5`–`189`; with FPS controls output duration. |
| `frames_per_second` | int, default `24` | Range `4`–`60`; duration = `num_frames / frames_per_second`. |
| `num_inference_steps` | int, default `28` | Range `1`–`50`; more steps can improve quality but take longer. |
| `guidance_scale` | float, default `6` | Range `0`–`20`; prompt adherence vs variety. |
| `seed` | nullable int | Same seed/prompt should reproduce similar output for the same model version. |
| `enable_safety_checker` | bool, default `true` | Keep enabled by default for content moderation. |
| `sync_mode` | bool, default `false` | Keep disabled by default; if true, output may return as data URI and not be available in request history. |

**Validation:** Require prompt and start-frame image; enforce numeric ranges, prompt/negative prompt lengths, image_size enum/object shape, and warn clearly that agentic generation can multiply cost.

**Verification:** Dry-run payload matches fal.ai docs/schema. Paid live test only after explicit user authorization.


### Task 7A: Add Hunyuan 3D 3.1 as the Replicate pilot for text-or-image 3D

**Objective:** Include the newer Replicate `tencent/hunyuan-3d-3.1` model in v0.4.0 before fal.ai work begins, using the verified schema and endpoint mode.

**Verified non-paid facts:**
- URL: `https://replicate.com/tencent/hunyuan-3d-3.1`
- Model ID: `tencent/hunyuan-3d-3.1`
- Description: “3D models with texture fidelity and geometry precision”
- Latest version ID: `a2838628b41a2e0ee2eb19b3ea98a40d75f8d7639bf5a1ddd37ea299bb334854`
- Replicate API page reports `usesVersionlessApi: true`
- Prediction creation should use `replicate.predictions.create(model="tencent/hunyuan-3d-3.1", input=...)`, not `version=...`
- Output schema is one URI string

**Expose all current input parameters:**

| Parameter | Type/default | Constraint / UX guidance |
|---|---|---|
| `prompt` | nullable string | Max 1024 chars. Use for text-to-3D. Mutually exclusive with `image`. |
| `image` | nullable URI | jpg/png/jpeg/webp; 128–5000 px per side; max 6 MB. Use for image-to-3D. Mutually exclusive with `prompt`. |
| `enable_pbr` | bool, default `false` | Plain label: “Generate realistic materials”. No effect for Geometry mode. |
| `face_count` | int, default `500000` | Range `40000`–`1500000`. Plain label: “Model detail / polygon count”. |
| `generate_type` | enum, default `Normal` | `Normal` textured model or `Geometry` white/untextured model. |

**Validation/UI:** Require exactly one of prompt/image; enforce enum/range/length locally; explain that PBR is ignored in Geometry mode. The form should visually require an input-source choice (“Text description” vs “Subject image”), then hide, disable, or clearly mark the inactive input so users cannot accidentally submit both text and image.

**History/UI:** Add `text_to_3d` and `image_to_3d` mode support; show the model as “newer Hunyuan option” in the 3D tab; keep Hunyuan3D 2.0 available unless deliberately deprecated.

**Verification:** Dry-run payload check only. Do not create a paid prediction unless explicitly authorized.

### Task 8: Update Streamlit model selector and provider messaging

**Objective:** Make provider visible but not the main burden on the user.

**Files:**
- Modify: `app.py`

**Verification:** Browser/manual QA confirms non-technical copy is understandable and provider/token missing states are clear.

### Task 9: Add provider-aware dry-run and diagnostics

**Objective:** Debug provider payload problems without spending money.

**Files:**
- Modify: `app.py`
- Modify/create: provider adapter diagnostics helpers

**Verification:** Dry-run shows provider, endpoint, payload, estimated/unknown cost, and required credentials without creating predictions.

### Task 10: Update docs after implementation

**Objective:** Keep version docs consistent after post-v1.0 fal.ai support lands.

**Files:**
- Modify: `README.md`
- Modify: `CHANGELOG.md`
- Modify: `ROADMAP.md`
- Modify: `DECISIONS.md`
- Modify: `REFERENCE.md`
- Modify: `AGENTS.md`

**Verification:** Docs clearly distinguish implemented fal.ai support from planned future provider/model expansion.

---

## Open questions before implementation

1. Confirm NVIDIA Cosmos 3 Super Image to Video should be the first fal.ai pilot implementation, not just the first documented candidate.
2. Does fal.ai require file upload/storage handling that differs from Replicate delivery URLs?
3. Does fal.ai expose job IDs/status URLs suitable for History links through the chosen Python/HTTP path?
4. Should Cosmos agentic generation be hidden behind an extra warning/confirmation because it can render multiple candidate videos?
5. Should unavailable-provider models be hidden by default or shown disabled for setup discovery?

Recommended defaults:

- Pilot with NVIDIA Cosmos 3 Super Image to Video first.
- Hide unavailable-provider models by default, with a small “provider setup” notice.
- Store provider/job/output metadata generically before adding multiple fal.ai models.
- Keep v1.0.0+ provider scope limited to Replicate + fal.ai, not unlimited provider expansion.

---

## Non-paid verification commands

Run after docs-only updates:

```bash
python -m compileall -q app.py src
uv run ruff check .
```

Run after implementation changes:

```bash
uv run python - <<'PY'
from src.models_config import VIDEO_MODELS, THREED_MODELS
models = list(VIDEO_MODELS.values()) + list(THREED_MODELS.values())
assert all(getattr(model, "provider", None) for model in models)
print("provider metadata present", len(models))
PY
```

Do not run paid Replicate or fal.ai predictions unless explicitly authorized with provider, model, and expected cost/scope.
