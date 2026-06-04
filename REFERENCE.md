# REFERENCE.md — Project Documentation Index

**Project**: ai-generation-ui
**Last updated**: 2026-06-04

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
    ├── IMPLEMENTATION_PLAN_PROVIDER_EXPANSION.md ← v1.0.0+ Replicate + fal.ai provider plan
    ├── IMPLEMENTATION_VER-0.5.0-TO-0.5.10.md ← Completed v0.5 UI/UX and History hardening notes
    ├── ITER_1_IMPLEMENTATION.md ← Historical as-built reference for v0.1/v0.2 baseline
    └── ROADMAP.md               ← Versioned plan toward v1.0.0
```

---

## Documents

### 1. README.md

**Purpose**: Project landing page — the first thing anyone reads.

**Contains**:
- What this project does (Streamlit UI for hosted video & 3D generation; Replicate now, fal.ai deferred until after v1.0.0)
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
- Current version: v0.5.10 History preview/layout hardening complete
- Summary of additions, changes, fixes, verification, and known limitations
- Historical v0.3.0, v0.2.0, and v0.1.0 entries

**Read when**: You want to know what version the project is at or what changed recently.

---

### 3. DECISIONS.md

**Purpose**: Design decisions record — why we chose each approach.

**Contains**:
- 11 resolved decisions with rationale, alternatives considered, and selected option
- Decision 1: Video models (Wan + Seedance)
- Decision 2: 3D models (Hunyuan3D, Hunyuan 3D 3.1, TRELLIS)
- Decision 3: UI layout (tabbed)
- Decision 4: Output display (inline viewer + automatic local copy)
- Decision 5: Parameter exposure (Balanced + Advanced)
- Decision 6: Error handling (toast + inline)
- Decision 7: File management (local output metadata and ignored generated files)
- Decision 8: API token management (.env)
- Decision 9: Cost tracking (static pricing table)
- Decision 10: Package management (uv)
- Decision 11: Replicate prediction endpoint mode (versionless vs versioned)
- Decision 12: Provider expansion through adapters
- Final model list with provider/model IDs

**Read when**: You're questioning why something is designed a certain way, or proposing a change that might conflict with a past decision.

---

### 4. AGENTS.md

**Purpose**: Context document for AI coding agents working on this repository.

**Contains**:
- Project overview and architecture
- Tech stack
- File storage policy (local output copies plus provider URLs)
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

### 6. IMPLEMENTATION_PLAN_PROVIDER_EXPANSION.md

**Purpose**: Implementation blueprint for v1.0.0+ expansion from Replicate-only to Replicate + fal.ai.

**Contains**:
- Provider-agnostic UI/provider-aware detail principles
- Proposed provider adapter architecture
- Provider-aware model config/history/result shapes
- post-v1.0 fal.ai credential/setup approach
- UI/UX plan for provider model cards, filters, dry-run previews, errors, and History
- Bite-sized implementation tasks and open questions

**Read when**: Planning or implementing post-v1.0 fal.ai support, provider-aware History, or provider model selection.

---

### 7. ITER_1_IMPLEMENTATION.md

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

### 8. ROADMAP.md

**Purpose**: Versioned roadmap — what comes next after v0.5.10.

**Contains**:
- Current version estimate: v0.5.10 History preview/layout hardening complete
- Pre-1.0 must-haves vs nice-to-haves
- v0.5.0-v0.5.10: UI shell polish, focused generation panels, media-role metadata, thumbnail/preview assets, gallery-first History, separate Gallery/Records redraw views, and inline History previews
- v0.6.0: safety, metadata audit, dry-run payloads, and schema drift checks
- v0.6.5: verified Replicate 3D/texture model expansion
- v0.8.0: v1.0 readiness and authorized smoke QA
- Post-1.0 exploration including History reuse, fal.ai/Meshy, masking/inpainting, and local mask helpers
- Priority ranking and v1.0.0 release criteria

**Read when**: Planning the next version. Roadmap items through v0.5.10 are implemented.

---

## Quick Reference by Task

| I want to... | Read this first |
|---|---|
| Understand the project | README.md |
| Run the app | README.md → Quick Start |
| Check current version/history | CHANGELOG.md |
| Know why a decision was made | DECISIONS.md |
| Add a new model | AGENTS.md, then ROADMAP.md / IMPLEMENTATION_PLAN_PROVIDER_EXPANSION.md → models_config.py |
| Modify the UI | UI_Decisions.md → ROADMAP.md → `src/ui/` modules |
| Add cost tracking for a new model/provider | AGENTS.md → Cost Tracking, pricing.py → provider plan |
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
| `src/models_config.py` | ModelConfig dataclasses for current models, provider metadata, and media-role metadata |
| `src/cost_tracker.py` | Backward-compatible SQLite init, insert, query, stats, thumbnail updates |
| `src/utils.py` | Format helpers, Replicate output URL normalization, safe serialization/upload metadata |
| `src/video_gen.py` | Replicate video generation wrappers |
| `src/threed_gen.py` | Replicate 3D generation wrappers |
| `pyproject.toml` | Dependencies and project config (uv) |
| `.env.example` | Template for provider API tokens |
| `.gitignore` | Git exclusions |
