# REFERENCE.md — Project Documentation Index

**Project**: ai-generation-ui
**Last updated**: 2026-06-03

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
    ├── ITER_1_IMPLEMENTATION.md ← Historical as-built reference for v0.1/v0.2 baseline
    └── ROADMAP.md               ← Versioned plan toward v1.0.0
```

---

## Documents

### 1. README.md

**Purpose**: Project landing page — the first thing anyone reads.

**Contains**:
- What this project does (Streamlit UI for Replicate video & 3D generation)
- Architecture diagram (ASCII)
- Tech stack summary
- Project directory structure
- Quick start instructions
- Current status

**Read when**: You're new to the project and want to understand what it is and how to run it.

---

### 2. CHANGELOG.md

**Purpose**: Version history — what changed in each standard-versioned release.

**Contains**:
- Current version: v0.2.0 local beta / capability-safe baseline
- Summary of additions, changes, fixes, and known limitations
- Historical v0.1.0 scaffold entry

**Read when**: You want to know what version the project is at or what changed recently.

---

### 3. DECISIONS.md

**Purpose**: Design decisions record — why we chose each approach.

**Contains**:
- 10 resolved decisions with rationale, alternatives considered, and selected option
- Decision 1: Video models (Wan + Seedance)
- Decision 2: 3D models (Hunyuan3D + TRELLIS)
- Decision 3: UI layout (tabbed)
- Decision 4: Output display (inline viewer + download, no autosave)
- Decision 5: Parameter exposure (Balanced + Advanced)
- Decision 6: Error handling (toast + inline)
- Decision 7: File management (preview-only, no local storage)
- Decision 8: API token management (.env)
- Decision 9: Cost tracking (static pricing table)
- Decision 10: Package management (uv)
- Final model list with Replicate IDs

**Read when**: You're questioning why something is designed a certain way, or proposing a change that might conflict with a past decision.

---

### 4. AGENTS.md

**Purpose**: Context document for AI coding agents working on this repository.

**Contains**:
- Project overview and architecture
- Tech stack
- File storage policy (no local output files in v0.2.0)
- Database schema
- Parameter categories (Balanced vs Advanced)
- Model identifiers
- Cost tracking architecture
- .gitignore rules
- uv workflow commands

**Read when**: You are an AI agent about to modify or extend this project. Load this first.

---

### 5. IMPLEMENTATION_PLAN.md

**Purpose**: Pre-implementation blueprint — the 20-step plan that guided the first build.

**Contains**:
- 5 phases × 20 steps with exact code snippets
- Phase 0: Bootstrap (project structure, .gitignore, venv, .env)
- Phase 1: Core Infrastructure (config, pricing, models_config, cost_tracker, utils)
- Phase 2: Video Generation (3 model functions)
- Phase 3: 3D Generation (2 model functions)
- Phase 4: Streamlit UI (3 tabs with full code)
- Phase 5: Polish (error handling, testing, cleanup)
- Verification commands for each step

**Read when**: You want to understand the planned approach vs what was actually built, or you're adding a new model and want to follow the same pattern.

**Note**: Some details differ from the final implementation (e.g., plan says `lib/`, actual code uses `src/`). See ITER_1_IMPLEMENTATION.md for the as-built version.

---

### 6. ITER_1_IMPLEMENTATION.md

**Purpose**: Historical as-built documentation for the v0.1/v0.2 baseline.

**Contains**:
- Directory structure (every file)
- Architecture diagram
- All 5 models with Replicate IDs, input modes, parameters
- Module-by-module reference (config, pricing, models_config, cost_tracker, video_gen, threed_gen, utils, app.py)
- End-to-end generation flow
- Cost tracking breakdown with per-model rates
- 10 design decisions mapped to implementations
- Dependencies
- What is NOT implemented (cross-reference to ROADMAP.md)
- Quick start

**Read when**: You need to understand the current codebase — what exists, how it works, where to find things.

---

### 7. ROADMAP.md

**Purpose**: Versioned roadmap — what comes next after v0.2.0.

**Contains**:
- Current version estimate: v0.2.0 local beta / capability-safe baseline
- v0.3.0: model capability matrix + schema-driven UX
- v0.4.0: durable output storage + permanent History preview
- v0.5.0: automated tests + optional live Replicate smoke tests
- v0.6.0+: model catalogue expansion and pricing refresh workflow
- Priority ranking and v1.0.0 release criteria

**Read when**: Planning the next version. Roadmap items after v0.2.0 are not implemented yet.

---

## Quick Reference by Task

| I want to... | Read this first |
|---|---|
| Understand the project | README.md |
| Run the app | README.md → Quick Start |
| Check current version/history | CHANGELOG.md |
| Know why a decision was made | DECISIONS.md |
| Add a new model | AGENTS.md, then ITER_1_IMPLEMENTATION.md → models_config.py |
| Modify the UI | ITER_1_IMPLEMENTATION.md → app.py reference |
| Add cost tracking for a new model | AGENTS.md → Cost Tracking, pricing.py |
| Plan the next version | ROADMAP.md |
| Understand the as-built code | ITER_1_IMPLEMENTATION.md |
| See the original plan | IMPLEMENTATION_PLAN.md |

---

## File Inventory (non-doc)

| File | Role |
|---|---|
| `app.py` | Streamlit entry point |
| `src/config.py` | .env loading, paths, token check |
| `src/pricing.py` | Static hardware pricing table |
| `src/models_config.py` | ModelConfig dataclasses for all 5 models |
| `src/cost_tracker.py` | SQLite init, insert, query, stats |
| `src/utils.py` | format helpers, Replicate output URL normalization, safe serialization/upload metadata |
| `src/video_gen.py` | generate_wan_2_7_t2v, generate_wan_2_5_i2v, generate_seedance_2_0 |
| `src/threed_gen.py` | generate_hunyuan3d_2, generate_trellis_2 |
| `pyproject.toml` | Dependencies and project config (uv) |
| `.env.example` | Template for Replicate API token |
| `.gitignore` | Git exclusions |
