# IMPLEMENTATION_VER-0.6.5.md — Replicate 3D and Texture Model Expansion

**Version**: v0.6.5
**Status**: Complete
**Date**: 2026-06-04

## Goal

Add four verified Replicate 3D/texture models using v0.6 dry-run safeguards, without paid predictions during development.

## Models added (verified 2026-06-04)

| Slug | Replicate ID | Endpoint | Workflow |
|------|--------------|----------|----------|
| `hunyuan3d-2mv` | `tencent/hunyuan3d-2mv` | versioned | Multiview image → 3D (`front_image` required) |
| `text2tex` | `adirik/text2tex` | versioned | `.obj` + prompt → textured mesh |
| `adirik-texture` | `adirik/texture` | versioned | Mesh file + prompt → textured mesh(es) |
| `rodin` | `hyper3d/rodin` | versioned | Text (+ optional reference image) → 3D |

Source pages:

- https://replicate.com/tencent/hunyuan3d-2mv
- https://replicate.com/adirik/text2tex
- https://replicate.com/adirik/texture
- https://replicate.com/hyper3d/rodin

## Implementation summary

- Extended `ModelConfig` with `file_input_params` and `required_file_params`.
- Added catalogue entries, payload builders, generation handlers, and registry entries.
- Extended Streamlit forms for mesh/multiview uploads and Rodin reference mode.
- Updated pricing hardware map (L40S estimates for new models).
- `adirik/texture` stores multiple output URIs in History when returned.

## Verification (non-paid)

```bash
python -m compileall -q app.py src
uv run ruff check .
uv run python scripts/model_diagnostics.py
```

No paid Replicate prediction was created.

## Next milestone

v0.7.0 — better errors, progress messaging, and recovery.