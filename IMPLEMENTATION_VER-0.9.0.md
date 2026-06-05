# IMPLEMENTATION_VER-0.9.0.md — v1.0 Readiness and Authorized Smoke QA

**Version**: v0.9.0 (planned)  
**Status**: Not implemented

**Prerequisite**: v0.8.0 Audio tab complete.

## Goal

Verify the Replicate-only personal baseline end to end before declaring v1.0.0 stable.

## Planned work

- Visible browser QA: Video, 3D, **Audio**, History Gallery, History Records, validation/empty states.
- With explicit user authorization and expected cost, one successful live smoke per workflow:
  - text-to-video, image-to-video, image-to-3D, text-to-3D, **music**, **speech**
- After each smoke: result preview, local save, History card/row, honest cost/status.
- Final docs alignment for v0.9.0 or v1.0.0 declaration.

## Tools

- `ALLOW_PAID_REPLICATE_SMOKE=1` and `scripts/paid_smoke.py` only when authorized.

## Acceptance criteria

- Browser QA covers all pages and major states.
- Authorized smoke passes or blockers documented honestly.
- Lightweight local checks pass without paid calls.
- Docs agree on scope and known limitations.

## Roadmap position

`v0.8.0` (audio) → **`v0.9.0` (smoke + QA)** → `v1.0.0`