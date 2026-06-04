# IMPLEMENTATION_VER-0.9.0.md — Replicate Audio Model Expansion (Planning)

**Version**: v0.9.0 (planned)
**Status**: **Research complete** — schema + pricing fetched 2026-06-04; **not implemented**
**Target**: Before v1.0.0 (after v0.7.0; before v0.8.0 smoke QA so smoke can cover audio)

**Prerequisite**: v0.6.0 dry-run/safety tooling; patterns from v0.6.10 workflow-aware UI.

---

## Authoritative data on disk

| Artifact | Purpose |
|----------|---------|
| `IMPLEMENTATION_VER-0.9.0-replicate-api-snapshot.json` | Latest version IDs, required fields, resolved OpenAPI params, output schema |
| `IMPLEMENTATION_VER-0.9.0-pricing-scrape.json` | Replicate page `billingConfig` tiers, p50 median, hardware |

**Fetch method**: `replicate.models.get()` + OpenAPI `Input` schema; Replicate HTML `billingConfig` (no paid predictions).
**Date checked**: 2026-06-04.

---

## Goal

Add **nine planned Replicate audio models** (three music, six speech) with a dedicated **Audio** area in the app, the same safety patterns as video/3D (validation, payload builders, preview request, history, local download), and plain-English controls.

Music and speech are different workflows — do not force one universal form.

---

## Models — verification status (2026-06-04)

### Music generation (3) — all verified

| Planned slug | Replicate ID | API required | Pricing (Replicate page) |
|--------------|--------------|--------------|---------------------------|
| `music-2.5` | `minimax/music-2.5` | `lyrics` | **$0.15** per output audio file; p50 ~$0.0096 |
| `stable-audio-2.5` | `stability-ai/stable-audio-2.5` | `prompt` | **$0.20** per output file; p50 ~$0.00047 |
| `lyria-2` | `google/lyria-2` | `prompt` | **$2** per 1000s output audio; p50 ~$0.0024 |

### Speech / TTS (6) — all verified

| Planned slug | Replicate ID | API required | Pricing (Replicate page) |
|--------------|--------------|--------------|---------------------------|
| `realtime-tts-2` | `inworld/realtime-tts-2` | `text` | **$0.035** per 1k input characters; p50 ~$0.00020 |
| `realtime-tts-1.5-max` | `inworld/realtime-tts-1.5-max` | `text` | **$0.035** per 1k input characters; p50 ~$0.00013 |
| `speech-2.8-hd` | `minimax/speech-2.8-hd` | `text` | **$0.10** per 1k input tokens; p50 ~$0.00020 |
| `speech-2.8-turbo` | `minimax/speech-2.8-turbo` | `text` | **$0.06** per 1k input tokens; p50 ~$0.00020 |
| `chatterbox` | `resemble-ai/chatterbox` | `text` | **$0.025** per 1k input characters; p50 ~$0.0087 |
| `elevenlabs-v3` | `elevenlabs/v3` | `text` | **$0.10** per 1k input characters; p50 ~$0.00016 |

Full param schemas: see `IMPLEMENTATION_VER-0.9.0-replicate-api-snapshot.json`.

---

## Product / UI direction (planned)

### Navigation

Extend query-param segmented nav (today: Video | 3D | History):

- **Audio** tab (or segment), with inner workflow filter:
  - **Make music** → music models only
  - **Generate speech** → speech models only
  - **All audio models**

### Model metadata

Extend `ModelConfig` (or parallel config) with:

- `model_type`: `"audio"` (new literal alongside `"video"` | `"3d"`)
- `audio_category`: `"music"` | `"speech"`
- `workflow_tags` for filter (e.g. `music`, `speech`)
- `workflow_archetype` examples: `text_to_music`, `text_to_speech`, plus model-specific paths from snapshot

### Outputs and storage

- Local directory: `outputs/audio/` (gitignored)
- History: `model_type` = `audio`; preview via `st.audio()`; download button for local file
- Preserve provider URL + `local_file_path` like video

### Safety (reuse v0.6.x)

- `replicate_payload.py` builders per slug
- `prepare_payload_for_model` / Preview request (no charge)
- `scripts/model_diagnostics.py` probes
- No live prediction unless user authorizes smoke (v0.8.0)

### Plain English

- Separate labels for music vs speech (prompt, voice, duration, lyrics, etc. — per verified schema)
- Tooltips for cost drivers (per file, per character, per token, per output second — per pricing scrape)

---

## Suggested implementation phases

| Phase | Scope |
|-------|--------|
| 1 | ~~Schema fetch~~ **Done** — JSON snapshots on disk |
| 2 | `models_config` + payload builders + registry + `audio_gen.py` (incl. `inworld/realtime-tts-1.5-max`) |
| 3 | Audio tab UI (workflow filter + per-category forms) |
| 4 | History/gallery support for audio assets |
| 5 | Docs version bump to 0.9.0; diagnostics |

---

## Acceptance criteria

- [x] All nine Replicate IDs verified; snapshots on disk
- [ ] Audio tab with music/speech workflow filter
- [ ] Each model: validation, dry-run payload, handler, pricing notes in `src/pricing.py`
- [ ] Successful local download + History row for audio output
- [ ] `model_diagnostics.py` passes without paid calls
- [ ] v0.8.0 smoke plan includes at least one authorized music + one speech run

---

## Out of scope for v0.9.0

- fal.ai audio providers (post-v1.0)
- Video model native-audio toggles (already on video models; separate from this milestone)
- Full DAW-style editing or stem mixing

---

## Roadmap position

```
v0.6.10 (done) → v0.7.0 (errors/progress) → v0.9.0 (audio) → v0.8.0 (smoke + QA) → v1.0.0
```

Post-1.0 deferred video UI for Aleph keyframes remains unchanged — see `ROADMAP.md`. Multi-reference upload controls were completed earlier in v0.6.11 for metadata-marked multi-file params.