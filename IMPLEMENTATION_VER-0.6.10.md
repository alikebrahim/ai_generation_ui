# IMPLEMENTATION_VER-0.6.10.md — Video Model Expansion + Workflow-Aware UI (Planning)

**Version**: v0.6.10 (planned)  
**Status**: **Complete** (implemented 2026-06-04)  
**Metadata verified**: 2026-06-04 (Replicate OpenAPI + model pages + `billingConfig` on pages)

**Prerequisite**: v0.6.0 dry-run/safety and v0.6.5 file-upload patterns.

### Authoritative data on disk

| Artifact | Purpose |
|----------|---------|
| `IMPLEMENTATION_VER-0.6.10-replicate-api-snapshot.json` | Latest version IDs, required fields, resolved OpenAPI params (incl. `$ref` enums) |
| `IMPLEMENTATION_VER-0.6.10-pricing-scrape.json` | Replicate page `billingConfig` tiers (USD per output second), p50 median, hardware label |

**Fetch method**: `replicate.models.get()` + OpenAPI `Input` schema; Replicate HTML `billingConfig` (no paid predictions).

---

## Goal

Add eight new Replicate video models (seven net-new slugs plus clearer separation from
existing `bytedance/seedance-2.0`) and evolve the Video tab so users can discover and
use **workflow-specific capabilities** (motion transfer, video edit, multimodal
references) without an API-dashboard feel.

**Note**: `bytedance/seedance-2.0` is already in the catalogue. This milestone adds
`bytedance/seedance-2.0-fast` as a separate, faster variant with a overlapping but not
identical schema.

---

## Models to add (verified 2026-06-04)

| Slug | Replicate ID | `workflow_archetype` | `workflow_tags` | API `required` | App validation (extra) |
|------|--------------|----------------------|-----------------|----------------|------------------------|
| `happyhorse-1.0` | `alibaba/happyhorse-1.0` | `text_or_image_video` | `text_to_video`, `image_to_video` | `[]` | `prompt` **or** `image` (at least one) |
| `kling-v3-omni` | `kwaivgi/kling-v3-omni-video` | `multimodal_video` | `text_to_video`, `image_to_video`, `edit_video`, `multimodal` | `prompt` | `generate_audio` XOR `reference_video`; `end_image` needs `start_image` |
| `seedance-2.0-fast` | `bytedance/seedance-2.0-fast` | `multimodal_video` | `text_to_video`, `image_to_video`, `multimodal` | `prompt` | `image`/`last_frame_image` XOR `reference_images`; refs need prompt tags `[ImageN]` etc. |
| `gen-4.5` | `runwayml/gen-4.5` | `text_or_image_video` | `text_to_video`, `image_to_video` | `prompt` | `duration` ∈ {5, 10} only |
| `dreamactor-m2.0` | `bytedance/dreamactor-m2.0` | `motion_transfer` | `motion_transfer` | `image`, `video` | No prompt param |
| `aleph-2` | `runwayml/aleph-2` | `video_edit` | `edit_video` | `prompt`, `video` | `keyframe_images`/`keyframe_positions` same length; video 2–30s, ≤16MB |
| `kling-v3-motion` | `kwaivgi/kling-v3-motion-control` | `motion_transfer` | `motion_transfer` | `image`, `video` | `prompt` optional (default `""`); max video length depends on `character_orientation` |
| `kling-o1` | `kwaivgi/kling-o1` | `multimodal_video` | `text_to_video`, `image_to_video`, `edit_video`, `multimodal` | `prompt` | Edit path: `reference_video` + `video_reference_type=base`; same mutual rules as Omni for end frame |

**Endpoint (all eight)**: `versionless` — `model=<replicate_id>` (matches existing Wan / Seedance 2.0).

**Output (all eight)**: single string URI (`format: uri`) → one `.mp4` (or provider URL).

### Pricing summary (Replicate page `billingConfig`, 2026-06-04)

Charges are **per second of output video** unless noted. Page also shows nominal compute `$0.0001/s` and hardware label `CPU` (use output-duration tiers for UI estimates).

| Slug | Tiers (USD / output second) | p50 median run |
|------|----------------------------|----------------|
| `happyhorse-1.0` | 720p **$0.14**; 1080p **$0.28** | $0.013 |
| `kling-v3-omni` | standard **$0.168**; +audio **$0.224**; pro **$0.224**; pro+audio **$0.28**; 4k **$0.42** (audio same) | $0.014 |
| `seedance-2.0-fast` | 480p **$0.07–0.08**; 720p **$0.15–0.17** (higher when `reference_videos` used / `video_in`) | $0.013 |
| `gen-4.5` | flat **$0.12** | $0.012 |
| `dreamactor-m2.0` | flat **$0.05** | $0.014 |
| `aleph-2` | flat **$0.336** (early access; no p50 yet) | — |
| `kling-v3-motion` | `std` **$0.07**; `pro` **$0.12** | $0.035 |
| `kling-o1` | `std` **$0.084**; std+video **$0.126**; `pro` **$0.112**; pro+video **$0.168** | $0.016 |

Full tier criteria: `IMPLEMENTATION_VER-0.6.10-pricing-scrape.json`.

### Per-model specification (API + page)

#### Happy Horse 1.0 (`happyhorse-1.0`)

- **Replicate ID**: `alibaba/happyhorse-1.0` — https://replicate.com/alibaba/happyhorse-1.0  
- **Version**: `d867e39d045d6449a05b8dd3bc10ea3acca69b99aebc34b831809c09cd523527`  
- **Modes**: T2V (`prompt`) or I2V (`image`, optional `prompt` for motion). `aspect_ratio` ignored when `image` set.  
- **Params**: `prompt` (≤2500 chars per page); `image` (jpg/png/bmp/webp, ≤10MB, 300px+ min side, AR 1:2.5–2.5:1); `resolution` enum `720p`|`1080p` (default `1080p`); `aspect_ratio` enum `16:9`,`9:16`,`1:1`,`4:3`,`3:4`; `duration` enum **3–15** (default 5); `seed` 0–2147483647 nullable.  
- **UI**: Balanced — prompt, image, resolution, duration, aspect_ratio, seed. No video upload.  
- **pricing_notes**: `720p $0.14/s; 1080p $0.28/s output (Replicate page 2026-06-04).`

#### Kling 3 Omni Video (`kling-v3-omni`)

- **Replicate ID**: `kwaivgi/kling-v3-omni-video` — https://replicate.com/kwaivgi/kling-v3-omni-video  
- **Version**: `460d4f46adf3c29abbcd8f42cf5434570da6b50a39ec4593f2006486b1dd3fba`  
- **Params**: `prompt` (required, max 2500); `mode` `standard`|`pro`|`4k` (default `pro`); `duration` 3–15 (ignored for edit/base video); `aspect_ratio` `16:9`|`9:16`|`1:1`; `start_image`, `end_image` (end requires start); `reference_images` (max 7, or 4 with video); `reference_video` (mp4/mov, 3–10s, 720–2160px, ≤200MB); `video_reference_type` `feature`|`base`; `generate_audio` (default false, **exclusive** with `reference_video`); `keep_original_sound` (default true); `multi_prompt` JSON (≤6 shots, durations sum to `duration`).  
- **Not in API**: README mentions `negative_prompt` — **not present** in OpenAPI (2026-06-04).  
- **media_roles**: `start_image` → “Start frame”; `end_image` → “End frame”; `reference_video` → “Reference or source video”; `reference_images` → “Reference images”.  
- **pricing_notes**: Tiered by `mode` + audio; see pricing table (up to $0.42/s for 4k).

#### Seedance 2.0 Fast (`seedance-2.0-fast`)

- **Replicate ID**: `bytedance/seedance-2.0-fast` — https://replicate.com/bytedance/seedance-2.0-fast  
- **Version**: `8a876cb913d631d9a4d47b3f777df7326d5571f37c49ed020fdcf4103240b158`  
- **Overlap with `seedance-2.0`**: Same multimodal pattern; Fast drops **1080p** (only `480p`|`720p`), shares ref arrays + `generate_audio`, adds no new required fields. Reuse payload builder patterns from Seedance 2.0 where param names match.  
- **Params**: `prompt` (required); `duration` **-1..15** (-1 = intelligent duration); `resolution` `480p`|`720p`; `aspect_ratio` includes `adaptive`; `image`, `last_frame_image` (mutually exclusive with `reference_images`); `reference_images` (≤9), `reference_videos` (≤3, total ≤15s), `reference_audios` (≤3, total ≤15s, needs image or video ref); `generate_audio` default true; `seed` nullable.  
- **pricing_notes**: $0.07–0.17/s depending on resolution and whether reference video inputs used.

#### Runway Gen-4.5 (`gen-4.5`)

- **Replicate ID**: `runwayml/gen-4.5` — https://replicate.com/runwayml/gen-4.5  
- **Version**: `2e10d5ae08888b39ed31c828003f4a5ddc89a7cdec3bc7a9926661e0d22cb034`  
- **Params**: `prompt` (required); `image` optional first frame; `duration` enum **5, 10** only; `aspect_ratio` `16:9`,`9:16`,`4:3`,`3:4`,`1:1`,`21:9`; `seed` nullable.  
- **UI**: Duration as dropdown (not slider). No resolution param (provider picks quality).  
- **pricing_notes**: `$0.12/s output (flat).`

#### Dreamactor M2.0 (`dreamactor-m2.0`)

- **Replicate ID**: `bytedance/dreamactor-m2.0` — https://replicate.com/bytedance/dreamactor-m2.0  
- **Version**: `b23bf8e6d5f31dd67ad219fac057fd43d3ac38fc58343025ab557be74a9450ca`  
- **Params**: `image` (required; JPEG/JPG/PNG, ≤4.7MB, 480×480–1920×1080); `video` (required; MP4/MOV/WebM, ≤30s, 200×200–2048×1440); `cut_first_second` boolean default true.  
- **file_input_params**: `image` → png,jpg,jpeg,webp; `video` → mp4,mov,webm.  
- **pricing_notes**: `$0.05/s output.`

#### Runway Aleph 2.0 (`aleph-2`)

- **Replicate ID**: `runwayml/aleph-2` — https://replicate.com/runwayml/aleph-2  
- **Version**: `67a723556e73936d6b4a1de17f10e033c94ee4310f8f80225511869b386a82e1`  
- **Early access**: ~49 runs on Replicate (2026-06-04); pricing/behavior may change.  
- **Params**: `video` (required; 2–30s, **≤16MB**); `prompt` (required); `keyframe_images` (≤5) + `keyframe_positions` (`first`|`last`|timestamp seconds, parallel arrays); `seed` nullable. Output AR matches input.  
- **Attribution**: Runway asks “Powered by Runway” + link when attributing (see page README).  
- **pricing_notes**: `$0.336/s output; treat estimates as provisional.`

#### Kling 3 Motion Control (`kling-v3-motion`)

- **Replicate ID**: `kwaivgi/kling-v3-motion-control` — https://replicate.com/kwaivgi/kling-v3-motion-control  
- **Version**: `15430b300f8c044e8f9e3567fd6daadf6d62e9bb0cee23fdb7969d3b26542f40`  
- **Params**: `image`, `video` (required); `prompt` optional default `""`; `mode` `std`|`pro` (720p vs 1080p); `character_orientation` `image` (max **10s** video) | `video` (max **30s**); `keep_original_sound` default true; video mp4/mov ≤100MB.  
- **pricing_notes**: `$0.07/s (std), $0.12/s (pro) output.`

#### Kling O1 (`kling-o1`)

- **Replicate ID**: `kwaivgi/kling-o1` — https://replicate.com/kwaivgi/kling-o1  
- **Version**: `6d5f2d4becc7f734d190d17f13f776229c359cafc1c1898d78945e8d87c57538`  
- **Dual use**: Same schema as Omni-lite — generation (T2V/I2V/refs) **or** edit (`reference_video` + `video_reference_type=base`).  
- **Params**: `prompt` (required); `mode` `std`|`pro`; `duration` enum 3–10 (T2V/I2V often 5/10 per description; 3–10 with feature video); `aspect_ratio`; `start_image`, `end_image`; `reference_images`; `reference_video`; `video_reference_type`; `keep_original_sound`.  
- **Page vs API**: README discusses `keep_audio` and `@Element1` notation — API field is `keep_original_sound`; element slots may be prompt-only on Replicate (no separate element URIs in OpenAPI).  
- **pricing_notes**: `$0.084–0.168/s depending on mode and whether video input used (see scrape JSON).

### Schema / documentation discrepancies (implementers)

| Topic | Notes |
|-------|--------|
| Kling Omni `negative_prompt` | Mentioned on marketing README, **absent** from OpenAPI |
| Kling O1 `keep_audio` | Page table name; API uses `keep_original_sound` |
| Aleph pricing | New model; no p50 on page yet |
| Dreamactor `image` copy | Page says “human subject”; examples include cartoons/animals — treat as general character image |
| Seedance 2.0 vs Fast | Catalogue keeps both; UI should hint Fast = quicker, 720p max, lower $/s |
| Hardware label `CPU` on pages | Billing display only; still use **output-duration** tiers for cost estimates in UI |

---

## UI problem statement

Today the Video tab assumes most models fit one layout:

- text prompt (+ optional single image upload);
- balanced numeric/enum controls;
- advanced expander;
- hidden list inputs for Seedance 2.0 references.

Eight new models break that assumption:

| Need | Models affected |
|------|-----------------|
| **Driving / source video upload** | Dreamactor, Kling motion, Aleph |
| **Two-role media** (character vs motion) | Dreamactor, Kling motion |
| **Multimodal reference arrays** | Kling Omni, Kling O1, Seedance Fast |
| **Video-edit framing** (edit, not generate) | Aleph, Kling O1 |
| **Strict duration enums** | Gen-4.5 (5/10 only), Happyhorse (3–15) |
| **Mode / quality tier** | Kling family (`std`/`pro`, `4k`) |

Without planning, the form either hides critical inputs or floods the panel with
every parameter for every model.

---

## Recommended UI architecture (v0.6.10)

### 1. Workflow-first entry (Video tab)

Add a lightweight **“What do you want to do?”** control above the model picker
(horizontal `st.radio` or segmented control). Suggested values:

| Workflow key | User label | Models shown |
|--------------|------------|--------------|
| `text_to_video` | Make a video from text | Happyhorse, Gen-4.5, Kling Omni, Kling O1, Seedance Fast (+ Wan T2V, Seedance 2.0) |
| `image_to_video` | Animate a start image | Happyhorse, Gen-4.5, Wan I2V, Seedance*, Kling* |
| `motion_transfer` | Copy motion from a reference video | Dreamactor, Kling motion control |
| `edit_video` | Change an existing video | Aleph, Kling O1, Kling Omni (base video ref) |
| `all` | Show all video models | Full list (default for power users) |

Filtering reduces a 11+ model dropdown to a short, intent-aligned list.

Persist selection in `st.session_state` (`video_workflow_filter`).

### 2. Model metadata: `workflow_archetype`

Extend `ModelConfig` with:

```python
workflow_archetype: Literal[
    "text_video",           # prompt required; optional image
    "text_or_image_video",  # prompt and/or image
    "multimodal_video",     # prompt + optional refs / start-end / audio
    "motion_transfer",      # image + driving video
    "video_edit",           # video + prompt (+ optional keyframes)
]
```

Optional: `workflow_tags: list[str]` for filter matching (`text_to_video`, etc.).

### 3. Per-archetype form layouts (not one universal form)

Keep **one** `render_generation_form()` entry point; branch on `model.workflow_archetype`
(and existing `generation_modes` where needed).

#### `text_or_image_video` (Happyhorse, Gen-4.5)

- Reuse Hunyuan-3D-style **Create from text / Create from image** radio when both paths
  are valid.
- Happyhorse: `required_one_of` prompt/image in validation.
- Gen-4.5: prompt required; image optional (I2V).

#### `multimodal_video` (Seedance Fast, Kling Omni, Kling O1, existing Seedance 2.0)

Split the right column into labeled sections (light `st.container(border=True)`):

1. **Text prompt** (required where schema says so)
2. **Start frame** — `image` / `start_image` (role-specific label from `media_roles`)
3. **End frame** (optional) — `end_image` / `last_frame_image` behind “Add end frame”
   checkbox
4. **Reference media (optional)** — collapsed expander “Reference images, videos, or
   audio” with:
   - Phase 1: caption “Coming soon” for `reference_*` arrays OR single-file stubs
   - Phase 2: multi-file uploaders with count limits from schema/docs

Seedance Fast aligns with existing Seedance 2.0 builder; share payload patterns.

Kling Omni / O1: expose `mode`, `generate_audio` / `keep_original_sound`,
`video_reference_type` in **Advanced** with plain labels (“Quality tier”, “Keep
original audio”, “How to use reference video”).

#### `motion_transfer` (Dreamactor, Kling motion)

Dedicated two-upload layout (always visible, not optional):

| Role | Label | Param | Types |
|------|-------|-------|-------|
| Character | Subject / character image | `image` | png, jpg, webp |
| Motion | Driving video | `video` | mp4, mov, webm |

Optional prompt (Kling motion) in text area below with caption “Optional — guide the
transfer”.

Advanced: `character_orientation`, `mode`, `cut_first_second` (Dreamactor), etc.

#### `video_edit` (Aleph, Kling O1 when filter = edit)

1. **Source video** (required) — single upload, `video`
2. **Edit instructions** — prompt text area (“Describe what to change”)
3. **Keyframes (optional)** — expander for Aleph `keyframe_images` + positions (Phase 2;
   validate array lengths match)

Kling O1 under edit workflow shares multimodal sections but emphasizes
`reference_video` + prompt.

### 4. Video file uploads

Extend `file_input_params` (from v0.6.5) to video MIME/types:

```python
file_input_params={
    "video": ["mp4", "mov", "webm"],
    "reference_video": ["mp4", "mov", "webm"],
}
```

Reuse `normalize_file_kwargs()` and dry-run summarization for uploaded videos.

Validation: max file size subtext (align with Replicate limits when documented);
no paid probe uploads.

### 5. Model picker presentation

**Option A (v0.6.10 default)**: Filtered `st.selectbox` + `format_func` showing
`display_name` only; workflow filter does the grouping.

**Option B (later)**: Two-step picker — workflow → model — if the list still feels long.

Do **not** rename model slugs; friendly `display_name` only, e.g. “Kling 3 Omni Video”.

Optional short **model card** caption under selector (one line from `output_notes` /
catalogue metadata).

### 6. Layout sketch (Video tab)

```
[ Video Generation header + caption ]

What do you want to do?  ( ) Text  ( ) Image  ( ) Motion  ( ) Edit  ( ) All

┌─ Preview panel (2/3) ─────────────┐  ┌─ Controls (1/3) ─────────────┐
│  Status / result / st.video       │  │ Model ▼                       │
│                                   │  │ ── Archetype-specific inputs ─│
│                                   │  │ [Prompt | Media sections]     │
│                                   │  │ Balanced controls             │
│                                   │  │ Cost estimate                 │
│                                   │  │ ▸ Advanced                    │
│                                   │  │ ▸ Preview request (no charge) │
│                                   │  │ [ Generate Video ]            │
└───────────────────────────────────┘  └───────────────────────────────┘
```

Motion/edit archetypes move **media uploads into the left column** (wide) when
two large assets are required; keep controls column for enums/sliders.

### 7. History and generation_mode

Add history `generation_mode` values as needed:

- `motion_transfer`
- `video_edit`
- `multimodal_video` (or keep `text_to_video` / `image_to_video` with tags)

Store which workflow filter was active for troubleshooting.

---

## Implementation phases (suggested)

### Phase 1 — Catalogue + simple models (lower UI risk)

- Happyhorse, Gen-4.5: archetype `text_or_image_video`
- Payload builders + registry + dry-run
- Mode selector + existing form patterns

### Phase 2 — Motion transfer

- Dreamactor, Kling motion control
- Video upload support + two-panel media layout
- Plain-English labels and validation

### Phase 3 — Video edit (single video)

- Aleph: prompt + video (+ dry-run); keyframe arrays deferred or advanced-only
- Kling O1: prompt-led edit path with optional refs in expander

### Phase 4 — Multimodal / arrays

- Seedance 2.0 Fast (reuse Seedance patterns)
- Kling Omni + Kling O1 full reference/start/end UI
- Decide minimum viable multi-upload (e.g. up to 4 reference images) vs. “use Preview
  request only until multi-upload ships”

### Phase 5 — Workflow filter + docs

- Video tab workflow radio
- Update README, CHANGELOG, DECISIONS model list
- `model_diagnostics.py` probes for all new slugs

---

## Acceptance criteria

- [x] All eight Replicate IDs verified and documented with `metadata_verified_date` (2026-06-04; see JSON snapshots)
- [x] Each model has `workflow_archetype`, `workflow_tags`, constraints, pricing notes (in this doc + scrape files)
- [x] Each model added to `src/models_config.py` with metadata fields
- [x] Workflow filter narrows the model list; “All” shows full catalogue (11 video models)
- [x] Motion and edit models expose **video** upload in plain English
- [x] Dry-run preview shows exact payload per archetype
- [x] `scripts/model_diagnostics.py` passes without paid calls
- [x] No paid prediction unless user explicitly authorizes smoke test
- [x] Single-file reference MVP for multimodal models; Aleph keyframes deferred

---

## Resolved scope decisions

| Topic | v0.6.10 choice | After v1.0.0 |
|-------|----------------|--------------|
| Reference arrays | Single reference image/video MVP in expander | **Post-1.0**: full multi-upload — `ROADMAP.md` → “Advanced video inputs” |
| Aleph keyframes | Not in UI (API supports them) | **Post-1.0**: keyframe editor UI — same roadmap section |
| Model picker | Workflow filter only | — |
| Seedance 2.0 vs Fast | Both in catalogue | — |

---

## Next after v0.6.10

v0.7.0 — errors/progress/recovery (can run in parallel only if v0.6.10 UI scope stays bounded).