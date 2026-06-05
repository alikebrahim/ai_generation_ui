# IMPLEMENTATION_VER-1.0.0.md — Stable Replicate-only personal baseline (UI + reliability)

**Version**: v1.0.0  
**Status**: Complete

**Summary**: v1.0.0 marks the comfortable Replicate-only personal local baseline. The major deliverable was the UI element & component readjustment pass (detailed in `UI_ASSESSMENT_PRE_V1.md`) to make Video / 3D / Audio + History feel like one coherent product, plus the critical circular import fix that was blocking reliable app startup in audio-first load paths.

No new models or features; focus was polish, consistency, and stability so day-to-day personal use "just works" and docs match behavior.

## Delivered

- **UI consistency & layout readjustment** (core of the pre-v1.0 assessment checklist):
  - All generation tabs now share the same skeleton: workflow filter → bordered "#### Model" card → workspace with creative inputs in the prominent left column (above live preview/result) and settings in the right column.
  - Prompt + primary subject/start/reference images (standard cases) + multimodal/rodin sections moved inside the left preview column, before the bordered result area. Special archetype media (motion transfer, video edit) remain grouped with the result as before.
  - Audio "Main input" (lyrics/text/prompt) moved into left column for breathing room + visual parity.
  - Preview red-border styling (via `.ai-prediction-preview-anchor` + CSS) now applies uniformly to Audio (previously only Video/3D).
  - Column ratio tuned to 1.9:1.6.
  - "Balanced controls" → "Main settings"; "Advanced controls" → "More settings (optional)".
  - One-line ★ legend for high-impact params.
  - Workflow filters changed from horizontal `st.radio` to `st.segmented_control` (matches global nav, better affordance).
  - Top chrome tightened (global page caption removed).
  - "Preview request (no charge)" → "Preview request payload (advanced)".
  - Existing example prompts / starter buttons removed from the Text prompt area (user direction: no need for them).

- **History information hierarchy + polish**:
  - Filters (search + new "Type" multi-select for Video/3D/Audio + model/provider/status) and Gallery/Records segmented view now render immediately after the view control.
  - The three top metrics + entire "By Model" per-model expanders moved to a bottom collapsed "Usage stats" expander.
  - "📋 Copy actions" expander → "View prompt & settings"; button labels updated to "Show prompt", "Show settings (JSON)", "Show seed (...)".
  - Thumbnail preview action made compact ("🔍 Preview", not a full-width button under every card); caption cleaned.

- **Critical bug fix (app stability)**:
  - Circular import resolved: `src/audio_models_config.py` → `src.models_config.py` (for ModelConfig) + bottom-of-`models_config.py` → `src.audio_models_config.py` (for AUDIO_MODELS to build ALL_MODELS).
  - Solution: moved `ModelConfig` dataclass + supporting types (`ModelType`, `ProviderName`, `ProviderEndpointMode`, `WorkflowArchetype`, `ParamConstraint`) to `src/domain.py` (already the home for domain dataclasses).
  - `audio_models_config.py` now imports the class only from `domain`.
  - `models_config.py` imports from `domain` at top and re-exports the names so **every** existing import path (`from src.models_config import ModelConfig`, relative imports in validation, specific model consts, etc.) remains 100% unchanged and continues to work.
  - `ALL_MODELS`, lookup dicts, and `get_*` helpers are now reliably populated regardless of import order.

- Verification and day-to-day readiness:
  - All lightweight non-paid checks (`compileall`, `ruff`, targeted import probes covering audio-first + full catalogue + registry verify + `import app`).
  - UI_ASSESSMENT_PRE_V1.md updated with implementation note.
  - Behavior + docs now agree on the v1.0.0 "sane UI" + Replicate-only personal baseline.

## Scope notes
- Replicate-only (fal.ai intentionally deferred until after v1.0.0; see `IMPLEMENTATION_PLAN_PROVIDER_EXPANSION.md` and `ROADMAP.md`).
- No change to internal `balanced_params` / model catalogue structure (only rendered UI headings and layout).
- Example prompts / starters were removed as part of the prompt-section work (user request).
- The circular import fix was essential for the baseline (the app would fail to start or load the Audio tab / registry in certain orders before the fix).

## Next
Post-1.0 work per `ROADMAP.md`: Aleph keyframes, fal.ai provider expansion (including Meshy exploration), further quality-of-life (History reuse, comparison, etc.).

## Verification performed
- `python -m compileall -q app.py src`
- `uv run ruff check .`
- Direct probes: `import app`, audio models + ALL_MODELS + lookups, ui tabs, generation_registry.verify_all_models_have_handlers()
- Manual Streamlit navigation / form / History smoke (no paid generations).

See `UI_ASSESSMENT_PRE_V1.md` (with implementation note), `CHANGELOG.md` (v1.0.0 entry), `ROADMAP.md`, and `README.md` for full context. All docs updated together for consistent "current v1.0.0" language.