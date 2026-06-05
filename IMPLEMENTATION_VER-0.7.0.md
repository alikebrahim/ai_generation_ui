# IMPLEMENTATION_VER-0.7.0.md — Better Errors, Progress, and Recovery

**Status**: Complete  
**Version**: 0.7.0  
**Source**: `ROADMAP.md` v0.7.0 section

## Goal

Keep failure and long-wait behavior understandable while preserving the minimal UI
direction from v0.5.x–v0.6.11.

## Delivered

| Area | Implementation |
|------|----------------|
| Error translation | `src/utils.py` — expanded `friendly_error_message`, `technical_error_detail` |
| Provider adapter | `src/providers/replicate.py` — `wait_for_prediction`, `prediction_result_dict`, `prediction_failure_message` |
| Progress UX | `src/generation_progress.py` — status labels, long-wait thresholds, `ProgressUpdater` |
| Shared UI | `src/ui/generation_panel.py` — preview panel + `run_model_generation` |
| Tabs | `src/ui/video_tab.py`, `src/ui/threed_tab.py` refactored to shared panel |
| Failure display | `src/ui/result_views.py` — link button + technical expander |
| Polling | `src/video_gen.py`, `src/threed_gen.py` use adapter wait/result helpers |

## Out of scope (per roadmap)

- **Cancel button**: Replicate supports cancel, but Streamlit blocks during a sync
  generation run; no cancel UI added in v0.7.0.
- **Audio tab**: v0.8.0 (complete).

## Acceptance criteria

- [x] Common errors are understandable without reading Python/HTTP exception details.
- [x] Generation panel shows waiting / running / done / failed states with elapsed time.
- [x] Provider job URL visible during polling and on failures.
- [x] Failed jobs preserve useful debugging information (expander + `error_detail`).
- [x] Docs and `pyproject.toml` version aligned at 0.7.0.

## Verification

```bash
python -m compileall -q app.py src
uv run ruff check .
uv run python -c "from src.utils import friendly_error_message; ..."
```

No paid Replicate predictions.

## Next milestone

**v0.8.0** — Replicate audio (complete); **v1.0.0** — personal baseline. See `IMPLEMENTATION_VER-0.8.0.md` and `ROADMAP.md`.