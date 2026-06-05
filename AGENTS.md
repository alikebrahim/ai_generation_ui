# AGENTS.md — AI Generation UI Project Guidelines

This document defines conventions, defaults, and constraints for this project. Follow these when implementing or modifying code.

## Authorization Rule

**No changes to project files may be made without explicit user authorization.** This means:
- Do not modify, create, or delete any file in this project unless the user has directly asked for it.
- If a conversation drift suggests a change might be useful, ask before acting.
- This overrides any tool's inclination to auto-fix or self-correct project files (e.g. auto-creating missing directories, auto-installing dependencies, auto-updating configs).
- Routine operational commands that do not alter project state (e.g. reading files, checking syntax, inspecting logs) are always fine.
- Do not edit `AGENTS.md` itself unless the user explicitly asks for a project
  operating-convention change. Treat it as governing instructions, not a normal
  implementation note.

## Project Scope

**IN SCOPE:**
- Video generation: Text-to-Video (T2V), Image-to-Video (I2V)
- 3D generation: Image-to-3D (I23D), Text-to-3D (T23D), multiview-to-3D, and mesh texturing via Replicate (`hunyuan3d-2`, `hunyuan3d-2mv`, `hunyuan-3d-3.1`, `trellis2`, `text2tex`, `texture`, `rodin`).
- **Audio generation (planned v0.9.0, before v1.0.0)**: music and speech/TTS via Replicate — see `IMPLEMENTATION_VER-0.9.0.md` and `ROADMAP.md` v0.9.0 (nine models: MiniMax, Stability, Lyria, Inworld, Resemble, ElevenLabs).
- Replicate API integration today; fal.ai provider integration, including Meshy exploration, is post-v1.0.0 work
- Streamlit-based web interface
- Cost tracking and generation history

**OUT OF SCOPE (until v0.9.0 ships):**
- Standalone music/speech tabs and audio-only model catalogue (tracked as v0.9.0; not implemented at v0.6.10)

**OUT OF SCOPE (unchanged):**
- Image generation (handled by ComfyUI workflows separately)
- Video-to-video transformations (future consideration)
- Local model inference (all generation via hosted providers such as Replicate/fal.ai)

## Project Nature and Quality Bar

This is a personal local web UI for hosted video/3D inference, currently Replicate-powered with fal.ai deferred until v1.0.0 or later, not a production SaaS
product. Optimize for a robust, pleasant local experience rather than enterprise
process.

Prioritize:
- Clear Streamlit UI/UX for personal generation workflows
- Avoiding obviously invalid or wasteful paid provider calls
- Plain-English explanations of model choices and parameters
- Useful generation history and honest cost/status messaging
- Simple, maintainable code and docs that future agents can understand

Do not over-optimize for:
- Enterprise-grade release engineering or CI/CD
- Exhaustive formal automated test suites
- Docker/deployment infrastructure
- Multi-user auth/user-management systems
- Local model inference stacks unless explicitly requested

A change is good enough when the UI behavior is clear, invalid paid calls are
blocked where practical, cost/history displays are not misleading, relevant docs
match the current behavior, and lightweight local verification passes.

## Intended Users and Plain-English UX

The eventual users include the project owner and his wife. Assume at least one
user is not comfortable with technical model-parameter terms.

For UI changes:
- Prefer labels and help text that explain what a control does in plain English.
- Keep raw model/API parameter names out of the main UI when a friendly label is
  available.
- Use tooltips/subtexts for model terms such as seed, guidance, steps, duration,
  aspect ratio, resolution, octree resolution, texture size, and pipeline type.
- Explain trade-offs practically: speed vs quality, cost impact, predictability,
  and when a setting can be left alone.
- Keep advanced controls collapsed unless they are commonly useful.
- Prefer “leave this alone unless…” guidance for advanced numeric settings.
- Use media role labels such as “start frame”, “subject image”, or “reference
  image” instead of generic “image” when the role is known.

Plain-language UX polish should be completed before v1.0.0.

## Personal-Project Verification

Formal automated tests are not required by default for this personal project.
Do not add pytest, CI, or a tests/ directory unless the user explicitly asks or
the project grows enough to justify it.

Prefer lightweight, non-paid verification:
- `python -m compileall -q app.py src`
- `uv run ruff check .` when ruff is configured
- Targeted Python probes for validation, pricing, history, and output parsing
- Manual Streamlit/browser QA for UI changes when feasible

Never create a paid Replicate or fal.ai prediction unless the user explicitly authorizes
the scope and expected cost. For normal development/review, use dry-run payload
inspection and local validation probes instead of live predictions.

## Documentation Consistency

Only update docs that materially changed. But when declaring a version or
milestone complete, update all relevant version docs together:

- `pyproject.toml`: project version
- `README.md`: current version, status, quick-start accuracy, and current scope
- `CHANGELOG.md`: entry for the completed version
- `ROADMAP.md`: completed milestone status and future milestone wording
- `IMPLEMENTATION_VER-*.md`: implementation status table / completion notes
- `DECISIONS.md`: only if an architectural or product decision changed
- `AGENTS.md`: only if project operating conventions changed

Do not leave docs in a mixed state where one file says “current”, another says
“planned”, and another says “pending”. Prefer one source of truth for detailed
requirements and link to it rather than duplicating long specs across many docs.

Follow the project's established documentation style only:
- Keep documentation in the existing project docs (`README.md`, `CHANGELOG.md`,
  `ROADMAP.md`, `DECISIONS.md`, and implementation-plan/version docs) rather than
  creating ad-hoc summary/report files.
- Match the tone, structure, and level of detail already used in nearby sections.
- Prefer updating the canonical document for a topic over adding a parallel file
  that restates the same status.
- Do not add standalone patch summaries, completion reports, or review notes unless
  the user explicitly asks for that artifact.

## Versioning Policy

Use lightweight pre-1.0 versioning as a personal planning aid:

- Patch versions: small fixes, UI polish, docs corrections, pricing updates
- Minor versions: meaningful UX, model-support, validation, history, or storage
  improvements
- v1.0.0: a comfortable Replicate-only personal baseline, not a public production guarantee

A version is complete when implemented behavior, local verification, and docs
agree.

### Docs on every patch or minor completion

When finishing a **patch (0.x.y)** or **minor (0.x.0)** version — not only majors —
update the documentation set in the same pass as the version bump. Do not leave
code at a new version while README/CHANGELOG/ROADMAP still describe the previous
release.

Minimum updates when declaring a patch or minor done:

- `pyproject.toml` — `version`
- `README.md` — current version, status, and quick-start accuracy if behavior changed
- `CHANGELOG.md` — new entry marked **Current**; prior entry marked superseded
- `ROADMAP.md` — milestone status and version table row
- `IMPLEMENTATION_VER-*.md` — add or update the version note when the milestone has
  substantial scope (typical for minors; use judgment for tiny patches)

Optional unless the topic changed: `DECISIONS.md`, `REFERENCE.md`, `AGENTS.md`.

Patch-only releases can use a short CHANGELOG entry; minors should also refresh
README status and ROADMAP “current version” wording.

## Tooling & Dependencies

### Package Management
- **uv** for dependency management and virtual environments
- `pyproject.toml` for project configuration
- No `requirements.txt` — uv uses pyproject.toml directly

### Core Dependencies (Latest Stable Versions)
```toml
streamlit = ">=1.58.0"       # Web UI framework
replicate = ">=1.0.7"        # Replicate API client
# fal.ai dependency/client will be added when post-v1.0 fal.ai provider support is implemented
python-dotenv = ">=1.2.2"    # Environment variable management
pillow = ">=10.0.0"          # Image processing
requests = ">=2.31.0"        # HTTP client for downloads
```

### Development Dependencies
```toml
ruff = ">=0.4.0"             # Fast Python linter
black = ">=24.0.0"           # Code formatter
```

### Environment Variables
- Use `.env` file (gitignored) for secrets
- `.env.example` for template
- Load via `python-dotenv` at app startup
- Never hardcode API tokens in code
- Provider credentials should be optional per provider: missing fal.ai credentials must not block Replicate-only use, and missing Replicate credentials must not block future fal.ai-only use.

## Architecture Decisions

### API / Provider Layer
- Current implementation uses the `replicate` Python package (official client).
- Post-v1.0 provider expansion adds fal.ai through a provider adapter layer; do not scatter provider-specific branches throughout `app.py`.
- Keep a single model catalogue in `src/models_config.py` with provider metadata for each model.
- Suggested future provider modules: `src/providers/base.py`, `src/providers/replicate.py`, `src/providers/fal.py`.
- One workflow wrapper per generation type can remain (`src/video_gen.py`, `src/threed_gen.py`) but should call provider adapters rather than knowing every API detail.
- Cost tracking module: `src/cost_tracker.py`.
- Each model/provider pair should have typed parameters or validated payload construction.
- API calls are async-friendly but start synchronous for simplicity.

### Cost Tracking & History
- Provider should be stored per generation (`replicate` or `fal`) so History can filter and troubleshoot by provider.
- Replicate provides `metrics` field in prediction responses with:
  - `predict_time`: Duration in seconds
  - `total_time`: Total time including queue
  - Hardware info (when available)
- Store generation metadata in SQLite database: `data/history.db`
- Track per-generation:
  - Model name, timestamp, prompt
  - Input parameters (resolution, duration, etc.)
  - Generation time, cost estimate
  - Output file path or provider delivery URL
  - Provider job/request ID and provider job URL when available
- Display stats in "History" tab:
  - Total spend per model
  - Total spend overall
  - Generation count per model
  - Recent generations gallery

### File Storage
- Successful provider outputs are saved locally after generation when possible.
- Provider delivery URLs are still preserved for immediate preview/troubleshooting, but Replicate URLs may expire after ~1 hour.
- Local output directories:
  - `outputs/videos/` for video files and TRELLIS preview videos
  - `outputs/models_3d/` for 3D model assets
  - `outputs/thumbnails/` reserved for future thumbnail/preview derivatives
- SQLite History persists provider URL plus local file metadata: `local_file_path`, `thumbnail_path`, and `file_size_bytes`.
- Failed local downloads must not lose the original provider URL or history metadata.
- Generated output files are local artifacts and should stay gitignored.

### Streamlit App Structure
- Single-page app with query-param-backed segmented navigation: Video | 3D | History (v0.9.0 adds **Audio**)
- **Video Tab**:
  - Model selector dropdown
  - Input form (text prompt, image upload if applicable)
  - Parameter sliders/toggles split into two categories:
    - **Balanced** (always visible): prompt, duration/resolution, seed, aspect ratio, negative prompt
    - **Advanced** (in collapsible expander): guidance scale, inference steps, scheduler type, motion strength
  - Generate button
  - Output display area (video player)
  - Download button for output file
  - Cost estimate display
- **3D Tab**: Same structure with 3D viewer instead of video player; current models include image-to-3D plus Hunyuan 3D 3.1 text-to-3D/image-to-3D
- **History Page**:
  - Summary stats (total spend, generations by model)
  - Gallery and Records as separate redraw views, not nested/concurrent tab bodies
  - Card view of recent generations with local/temporary/missing-local indicators
  - Filterable records table for troubleshooting and lookup
  - Local preview/download/open buttons for existing local files when practical
- Use `st.session_state` to persist form inputs during generation

### UI Components
- **Video display**: `st.video()` — native Streamlit, battle-tested
- **3D display**: Google's `<model-viewer>` via `st.components.v1.html()`
  - Inject HTML/JS with model URL as parameter
  - Supports rotation, zoom, lighting
- **Image upload**: `st.file_uploader()` with preview
- **Progress**: `st.progress()` for polling Replicate API status
- **Error handling**: `st.error()` with user-friendly messages
- **Cost display**: Show estimated cost before generation, actual after

### Code Style
- Python 3.11+
- Type hints on all function signatures
- Docstrings on public functions
- Black formatter, 88 char line length
- Ruff for linting (configured in pyproject.toml)

### Configuration
- API tokens via `.env` file (loaded with python-dotenv)
- Do not require all provider tokens at startup; unavailable providers should be hidden or disabled with clear setup copy.
- No hardcoded Replicate model versions — use `latest` alias or fetch version list where appropriate.
- Model configurations in `src/models_config.py` should map model names to provider identifiers, capability flags, parameter groups, endpoint metadata, and defaults.

### Adding or Updating Models
- Before adding any Replicate model, fetch current authoritative facts from `replicate.com` and/or the Replicate API for the exact model ID. Verify available parameters, required fields, ranges/enums/defaults, endpoint mode (`model=` versionless vs `version=` latest-version path), output schema, hardware, and pricing.
- Before adding any fal.ai model, fetch current authoritative facts from the fal.ai model page and OpenAPI schema for the exact endpoint ID. Verify available parameters, required fields, output schema, queue/endpoint behavior, pricing, and any cost multipliers such as duration, candidate count, or agentic generation.
- Keep provider parameter schemas as canonical repo references under
  `schemas/<provider>/<model-name>.json` (currently `schemas/replicate/*.json`).
  Each schema card should include the exact provider model ID, source/API URL,
  fetch timestamp, endpoint mode, input schema, and output schema when available.
- When adding a new model or changing a model's payload/UI parameters, fetch or
  refresh its schema card first and then make `src/models_config.py`, payload
  builders, validation, and UI file-upload keys match that schema. Do not rename
  provider parameters to friendlier terms in payloads; keep friendly labels in
  `media_roles`/UI copy while preserving exact API keys such as `image` vs
  `start_image`.
- Do not add a model from memory, stale notes, provider marketing summaries, or another model's schema. Record source URLs and date checked in the relevant roadmap/implementation notes when adding model support.
- Keep pricing honest: if current pricing cannot be verified, display “Cost unknown” or an explicit approximate estimate rather than pretending precision.
- Never create a paid provider prediction just to discover schema or pricing. Use provider docs/API metadata, dry-run payload inspection, and local validation probes unless the user explicitly authorizes a paid smoke test with expected cost/scope.
- v0.6.5 added `tencent/hunyuan3d-2mv`, `adirik/text2tex`, `adirik/texture`, and `hyper3d/rodin` (schemas verified 2026-06-04; see `IMPLEMENTATION_VER-0.6.5.md`).
- v0.6.10 added eight Replicate video models and workflow-aware Video tab UI (`IMPLEMENTATION_VER-0.6.10.md`).
- v0.9.0 (planned, before v1.0.0) adds nine Replicate audio models and an Audio tab; see `IMPLEMENTATION_VER-0.9.0.md`. Fetch schemas before implementing.
- Meshy is planned as post-v1.0 fal.ai/provider-expansion work; treat its params/pricing/output shapes as unknown until verified from fal.ai at implementation time.
- **Live smoke QA** (v0.8.0): optional real paid Replicate runs, one per workflow, with explicit user authorization — not part of routine dev. Use `ALLOW_PAID_REPLICATE_SMOKE=1` and `scripts/paid_smoke.py` only when authorized.

## Naming Conventions

- **Files**: `snake_case.py`
- **Functions**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Streamlit pages**: Single file `app.py` (not multi-page structure)

## Error Handling Strategy

1. **API errors**: Catch provider-specific errors (`replicate.exceptions.ReplicateError`, fal.ai errors), show friendly message
2. **Network errors**: Retry up to 3 times with exponential backoff for transient failures
3. **Invalid inputs**: Validate before API call, show `st.error()` immediately
4. **File errors**: Ensure output directory exists, catch write permission errors
5. **Cost calculation**: If metrics missing, show "Cost unknown" rather than crashing

## Verification Approach

- No formal automated test suite is required by default.
- Prefer lightweight non-paid checks:
  - compile/import checks
  - configured lint
  - targeted Python probes for validation, pricing, history, and output normalization
  - manual Streamlit/browser QA when UI changes are made and a token/runtime is available
- Live Replicate/fal.ai generation checks are manual and opt-in because they may cost money.
- Do not add pytest/CI unless the user explicitly asks or the project scope changes.

## Performance Guidelines

- **Video generation**: 30 seconds to 5 minutes typical
  - Poll provider API every 5 seconds
  - Show progress bar with estimated time
- **3D generation**: 1 to 10 minutes typical
  - Poll every 10 seconds
  - Show spinner with status message
- **File downloads**: Save successful provider outputs locally after generation; use Streamlit download buttons for local files when practical and preserve provider URLs as fallback.
- **History queries**: Index SQLite database on model_name and timestamp for fast filtering

## Security

- Never log or display provider API tokens
- `.env` file must be in `.gitignore`
- Validate file uploads (size, type) before processing
- Sanitize user prompts (basic length limit, no code injection)

## Dependencies Installation

```bash
# Create venv and install deps
uv venv
uv pip install -e .

# For development
uv pip install -e ".[dev]"
```

## Git Workflow

- Commit messages: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`
- One feature per branch
- No `main` branch protection initially (solo dev)
- `.gitignore` must include: `.env`, `.venv/`, `__pycache__/`, `*.pyc`, `data/`, `outputs/`

## Future Extensibility

Design with these future additions in mind (but don't implement now):
- Rerun/remix from History
- Side-by-side model comparison
- Batch generation (multiple prompts)
- ComfyUI integration for image preprocessing
- Local model support (Hunyuan3D-2 on local GPU)
- Export history to CSV/JSON
- Post-v1.0 fal.ai provider expansion including Meshy

## Deployment

- Local development only for now
- Run with: `streamlit run app.py`
- Default port: 8501
- No Docker initially (keep it simple)

## Database Schema (for history tracking)

```sql
CREATE TABLE generations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    model_type TEXT NOT NULL,  -- 'video' or '3d'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    prompt TEXT,
    input_image_path TEXT,  -- NULL for text-only
    parameters_json TEXT,   -- JSON string of generation params
    replicate_url TEXT NOT NULL,
    predict_time_seconds REAL,
    total_time_seconds REAL,
    estimated_cost_usd REAL,
    status TEXT,  -- 'success', 'failed', 'cancelled'
    provider TEXT,
    replicate_prediction_id TEXT,
    replicate_prediction_url TEXT,
    generation_mode TEXT,
    local_file_path TEXT,
    thumbnail_path TEXT,
    file_size_bytes INTEGER
);

CREATE INDEX idx_model_name ON generations(model_name);
CREATE INDEX idx_timestamp ON generations(timestamp);
```
