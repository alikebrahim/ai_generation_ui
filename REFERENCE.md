# REFERENCE.md — Project Documentation Index

**Project**: ai-generation-ui
**Last updated**: 2026-06-04
**Current version**: v0.6.5

---

## Documentation Map

```
REFERENCE.md   ← YOU ARE HERE (index of everything)
    │
    ├── README.md                ← Start here: what, why, how to run
    ├── CHANGELOG.md             ← Version history and current release notes
    ├── DECISIONS.md             ← Why we chose what we chose
    ├── AGENTS.md                ← Technical context for AI agents working on this repo
    ├── IMPLEMENTATION_PLAN.md   ← Step-by-step build guide (pre-implementation blueprint)
    ├── IMPLEMENTATION_PLAN_ARCHITECTURE_REFACTOR.md ← v0.4.x refactor plan
    ├── IMPLEMENTATION_PLAN_PROVIDER_EXPANSION.md ← v1.0.0+ Replicate + fal.ai plan
    ├── IMPLEMENTATION_VER-0.4.3-TO-0.4.9.md ← Completed architecture refactor
    ├── IMPLEMENTATION_VER-0.5.0-TO-0.5.10.md ← Completed UI/UX + History hardening
    ├── IMPLEMENTATION_VER-0.6.0.md ← Safety, dry-run, schema diagnostics
    ├── IMPLEMENTATION_VER-0.6.5.md ← 3D/texture model expansion
    ├── IMPLEMENTATION_VER-0.6.10.md ← Planned video expansion + workflow UI
    ├── UI_Decisions.md            ← v0.5 UI/UX design decisions
    ├── ITER_1_IMPLEMENTATION.md ← Historical as-built reference (v0.1/v0.2)
    └── ROADMAP.md               ← Versioned plan toward v1.0.0
```

---

## Current release (v0.6.5)

- **10 Replicate models**: 3 video + 7 3D/texture
- **Safety**: Preview request (no charge), `replicate_payload.py`, `schema_diagnostics.py`
- **CLI probes**: `scripts/model_diagnostics.py` (non-paid), `scripts/paid_smoke.py` (opt-in paid)
- **Pre-1.0 remaining**: v0.7.0 errors/progress, v0.8.0 authorized live smoke QA, plain-English UX polish

---

## Documents

### 1. README.md

**Purpose**: Project landing page — the first thing anyone reads.

**Contains**: What the app does, model list, architecture, quick start, project structure, status.

**Read when**: You're new to the project or need run instructions.

---

### 2. CHANGELOG.md

**Purpose**: Version history — what changed in each release.

**Current**: v0.6.5 (3D/texture expansion). v0.6.0 (dry-run/safety). v0.5.10 (History layout).

**Read when**: You need the authoritative version number or recent changes.

---

### 3. DECISIONS.md

**Purpose**: Design decisions with rationale.

**Read when**: Questioning why something is designed a certain way.

---

### 4. AGENTS.md

**Purpose**: Conventions for AI agents and contributors.

**Contains**: Scope, versioning + **docs on every patch/minor**, model-add rules, architecture, verification, live smoke QA note.

**Read when**: Modifying code or adding models.

---

### 5. ROADMAP.md

**Purpose**: Versioned product roadmap toward v1.0.0.

**Current milestone complete**: v0.6.10. **Next planned**: v0.7.0 (errors/progress/recovery).

**Read when**: Planning the next version.

---

### 6. IMPLEMENTATION_VER-0.6.0.md / IMPLEMENTATION_VER-0.6.5.md

**Purpose**: As-built notes for the v0.6.x milestones (dry-run tooling and new 3D models).

**Read when**: Implementing or debugging safety features or the four v0.6.5 models.

---

### 7. IMPLEMENTATION_PLAN_PROVIDER_EXPANSION.md

**Purpose**: Post-v1.0 fal.ai / multi-provider expansion blueprint.

**Read when**: Planning provider expansion after the Replicate-only baseline.

---

### 8. ITER_1_IMPLEMENTATION.md

**Purpose**: Historical as-built docs for early baseline (partially superseded).

**Read when**: Tracing early architecture; cross-check against CHANGELOG for current behavior.

---

## Quick Reference by Task

| I want to... | Read this first |
|---|---|
| Understand the project | README.md |
| Run the app | README.md → Quick Start |
| Check current version | CHANGELOG.md (top entry) |
| Know why a decision was made | DECISIONS.md |
| Add a new model | AGENTS.md → `models_config.py` → `IMPLEMENTATION_VER-*.md` pattern |
| Debug payload before paying | UI Preview request or `prepare_generation_request()` |
| Non-paid schema check | `uv run python scripts/model_diagnostics.py` |
| Authorized live smoke test | ROADMAP v0.8.0 → `scripts/paid_smoke.py` |
| Plan the next version | ROADMAP.md |

---

## Local verification (no paid calls)

```bash
python -m compileall -q app.py src
uv run ruff check .
uv run python scripts/model_diagnostics.py
```