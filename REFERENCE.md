# REFERENCE.md — Project Documentation Index

**Project**: ai-generation-ui
**Last updated**: 2026-06-05
**Current version**: v0.8.0

---

## Documentation Map

```
REFERENCE.md   ← YOU ARE HERE (index of everything)
    │
    ├── README.md                ← Start here: what, why, how to run
    ├── CHANGELOG.md             ← Version history and current release notes
    ├── DECISIONS.md             ← Why we chose what we chose
    ├── AGENTS.md                ← Technical context for AI agents working on this repo
    ├── ROADMAP.md               ← Versioned plan toward v1.0.0 (source of truth for milestones)
    ├── IMPLEMENTATION_VER-0.6.0.md ← Safety, dry-run, schema diagnostics
    ├── IMPLEMENTATION_VER-0.6.5.md ← 3D/texture model expansion
    ├── IMPLEMENTATION_VER-0.6.10.md ← Video expansion + workflow UI (complete)
    ├── IMPLEMENTATION_VER-0.7.0.md ← Errors, progress, recovery
    ├── IMPLEMENTATION_VER-0.8.0.md ← Audio milestone (complete)
    ├── IMPLEMENTATION_VER-0.9.0-replicate-api-snapshot.json ← audio OpenAPI fetch
    ├── IMPLEMENTATION_VER-0.9.0-pricing-scrape.json ← audio pricing fetch
    ├── IMPLEMENTATION_PLAN_PROVIDER_EXPANSION.md ← v1.0.0+ Replicate + fal.ai plan
    ├── IMPLEMENTATION_VER-0.4.3-TO-0.4.9.md ← Completed architecture refactor
    ├── IMPLEMENTATION_VER-0.5.0-TO-0.5.10.md ← Completed UI/UX + History hardening
    ├── UI_Decisions.md            ← v0.5 UI/UX design decisions
    └── ITER_1_IMPLEMENTATION.md ← Historical as-built reference (v0.1/v0.2)
```

---

## Current release (v0.8.0)

- **Audio** tab: 9 models (3 music + 6 speech), workflow filter, `st.audio()` preview.
- **Video** (11) and **3D / texture** (7) unchanged from v0.6.10 / v0.6.5.
- Gallery-first History, durable local outputs, preview request + dry-run + diagnostics.

## Previous release (v0.7.0)

- Clearer errors, progress messaging, recovery hints, shared generation panel.

| Area | Count | Notes |
|------|-------|--------|
| Video | 11 | Workflow filter; motion/edit/multimodal layouts |
| 3D / texture | 7 | Mesh/multiview uploads |
| Audio | 9 | Music + speech; see `IMPLEMENTATION_VER-0.8.0.md` |

**Safety**: Preview request (no charge), `replicate_payload.py`, `schema_diagnostics.py`
**CLI**: `scripts/model_diagnostics.py` (non-paid)

---

## Path to v1.0.0

| Milestone | Status |
|-----------|--------|
| v0.7.0 — errors, progress, recovery | Complete |
| v0.8.0 — audio (music + speech) | Complete |
| v1.0.0 — stable Replicate-only baseline | Release target (use the app; align docs when ready) |

**Post-1.0**: Aleph keyframes UI and fal.ai — `ROADMAP.md`. Multi-reference uploads are available in v0.6.11 for metadata-marked multi-file params.

---

## Documents

### README.md

Landing page: models, architecture, quick start, status.

### CHANGELOG.md

Authoritative shipped versions. See **Planned milestones** at the top for v1.0.0+.

### ROADMAP.md

Product direction, pre-1.0 tiers, per-version specs, version table.

### IMPLEMENTATION_VER-0.8.0.md

Shipped audio milestone.

| Snapshot | Role |
|----------|------|
| `IMPLEMENTATION_VER-0.9.0-replicate-api-snapshot.json` | OpenAPI params, version IDs, required fields |
| `IMPLEMENTATION_VER-0.9.0-pricing-scrape.json` | `billingConfig`, p50, per-file/character/token pricing |

**Speech catalogue** includes `inworld/realtime-tts-2` and `inworld/realtime-tts-1.5-max` among six speech models.

### AGENTS.md

Scope (video, 3D, audio), conventions, verification, docs-on-release policy.

---

## Quick Reference by Task

| I want to... | Read this first |
|---|---|
| Understand the project | README.md |
| Run the app | README.md → Quick Start |
| Check current version | CHANGELOG.md (top entry) |
| Plan next work | ROADMAP.md → “Pre-1.0 path at a glance” |
| Add video/3D model | AGENTS.md → `IMPLEMENTATION_VER-*.md` pattern |
| Add audio model | `IMPLEMENTATION_VER-0.8.0.md` + JSON snapshots |
| Debug payload before paying | Preview request / `prepare_generation_request()` |
| Non-paid schema check | `uv run python scripts/model_diagnostics.py` |

---

## Local verification (no paid calls)

```bash
python -m compileall -q app.py src
uv run ruff check .
uv run python scripts/model_diagnostics.py
```