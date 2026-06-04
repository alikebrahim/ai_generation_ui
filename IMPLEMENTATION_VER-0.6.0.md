# IMPLEMENTATION_VER-0.6.0.md — Safety, Metadata Audit, Dry-Run, Schema Diagnostics

**Version**: v0.6.0  
**Status**: Complete  
**Date**: 2026-06-04

## Goal

Make paid Replicate calls safer and make model/schema problems easy to diagnose without spending money, using the v0.4.9 request-preparation hook and a current metadata audit.

## Delivered

| Area | Implementation |
|------|----------------|
| Payload builders | `src/replicate_payload.py` — shared input dict builders used by generation handlers and dry-run |
| Dry-run service | `UnifiedGenerationService.prepare_generation_request()` — validation, endpoint summary, cost label, JSON payload preview |
| Schema diagnostics | `src/schema_diagnostics.py` — local vs remote OpenAPI comparison (optional fetch with token) |
| UI preview | `src/ui/request_preview.py` + Video/3D forms — “Preview request (no charge)” expander |
| CLI probes | `scripts/model_diagnostics.py`, `scripts/paid_smoke.py` (requires `ALLOW_PAID_REPLICATE_SMOKE=1`) |
| Metadata audit | All six models: `metadata_verified_date`, `replicate_page_url`, `pricing_notes`, `output_notes` |

## Verification (non-paid)

```bash
python -m compileall -q app.py src
uv run ruff check .
uv run python scripts/model_diagnostics.py
```

No paid Replicate prediction was created during implementation.

## Known limitations

- Remote schema warnings for `requires_image` vs Replicate `required: []` on some 3D models are informational (Replicate allows optional image in schema while the app enforces image in UI).
- Paid smoke remains manual via `scripts/paid_smoke.py` with explicit env opt-in (v0.8.0 will run full workflow QA).

## Next milestone

v0.7.0 — better errors, progress messaging, and recovery (see `ROADMAP.md`).