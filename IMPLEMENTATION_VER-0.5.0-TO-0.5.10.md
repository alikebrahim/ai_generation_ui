# v0.5.0-v0.5.10 UI/UX Baseline — Complete

**Status: ALL Patches Complete** ✅
**Verification**: `python -m compileall -q app.py src` + `uv run ruff check .`
**Runtime smoke**: Streamlit AppTest render against existing local History rows
**Date**: 2026-06-04

---

## Overview

Completed the v0.5 UI/UX series that turned the app into a cleaner, more focused local creative workspace. The app now has a shared shell style, focused generation/result panels, human-readable media-role metadata, gallery-first History views, separate Gallery/Records redraw views, inline History previews, and updated docs/version alignment.

The work kept the Replicate-only product scope intact while making the visible UI feel more coherent and easier to use.

---

## Patches Completed

### v0.5.0 — App shell styling and layout reliability ✅

**Files**: `src/ui/style.py`, `app.py`, `src/ui/forms.py`, `src/ui/video_tab.py`, `src/ui/threed_tab.py`, `src/ui/history_tab.py`

**Changes**:
- Added shared shell styling for the top-level app.
- Tightened header/tab spacing and improved overall layout reliability.
- Kept the visible UI minimal and familiar.

**Benefit**: The app looks cleaner and the core controls are easier to scan.

---

### v0.5.1 — Focused generation panel for Video ✅

**Files**: `src/ui/video_tab.py`, `src/ui/result_views.py`

**Changes**:
- Reworked the Video tab into one clear generation/result panel.
- Kept running status and result output in the same place.
- Surface failures inline instead of sending users elsewhere.

**Benefit**: Video generation is easier to follow and recover from.

---

### v0.5.2 — Focused generation panel for 3D ✅

**Files**: `src/ui/threed_tab.py`, `src/ui/result_views.py`

**Changes**:
- Reworked the 3D tab into a matching focused panel.
- Kept progress, result, and error display together.
- Preserved the interactive preview flow for successful generations.

**Benefit**: 3D generation feels consistent with Video and is easier to read.

---

### v0.5.3 — Hunyuan 3D 3.1 mode selector ✅

**Files**: `src/ui/forms.py`, `src/models_config.py`

**Changes**:
- Added clear mode selection for text-to-3D vs image-to-3D.
- Showed only the relevant input for the selected mode.
- Blocked invalid combinations before any paid call.

**Benefit**: Hunyuan 3D 3.1 is easier to understand and harder to misuse.

---

### v0.5.4 — Media-role metadata ✅

**Files**: `src/models_config.py`, `src/ui/forms.py`, `src/domain.py`

**Changes**:
- Added human-readable media-role metadata to model config.
- Used role-specific wording such as subject image and start frame.
- Reduced generic "upload image" language where a better label exists.

**Benefit**: The form now explains inputs in plain English.

---

### v0.5.5 — Video thumbnails for History ✅

**Files**: `src/storage_service.py`, `src/ui/history_tab.py`, `src/video_gen.py`

**Changes**:
- Added first-frame/preview thumbnail handling for video outputs when available.
- Displayed thumbnails on History cards.
- Kept fallback behavior when a thumbnail cannot be created.

**Benefit**: History is much easier to scan visually.

---

### v0.5.6 — 3D previews and multi-asset History ✅

**Files**: `src/storage_service.py`, `src/threed_gen.py`, `src/output_asset.py`

**Changes**:
- Preserved multiple useful assets from 3D generations.
- Captured preview assets alongside primary 3D outputs when available.
- Kept the interactive viewer as the detail/result experience.

**Benefit**: Multi-asset 3D results are represented more completely.

---

### v0.5.7 — History gallery/records split ✅

**Files**: `src/ui/history_tab.py`, `src/history_service.py`

**Changes**:
- Split History into Gallery and Records views.
- Kept filter controls and summary cards available.
- Improved wording around local files, temporary links, and downloads.

**Benefit**: History is easier to browse and troubleshoot.

---

### v0.5.8 — Gallery-first History layout ✅

**Files**: `src/ui/history_tab.py`

**Changes**:
- Made Gallery the default History view.
- Kept Records accessible for lookup and debugging.
- Preserved download/open actions and asset-awareness messaging.

**Benefit**: History now works like a visual gallery first and a table second.

---

### v0.5.9 — Final UX hardening and docs alignment ✅

**Files**: `README.md`, `CHANGELOG.md`, `ROADMAP.md`, `REFERENCE.md`, `DECISIONS.md`, `pyproject.toml`

**Changes**:
- Updated version/docs to reflect the v0.5.9 milestone.
- Aligned the roadmap and reference docs with the completed UI baseline.
- Cleaned up the file-management decision so it matches durable local output behavior.

**Benefit**: The code and docs agreed on the v0.5.9 milestone before the follow-up History hardening pass.

---

### v0.5.10 — History preview and layout hardening ✅

**Files**: `app.py`, `src/ui/history_tab.py`, `README.md`, `CHANGELOG.md`, `ROADMAP.md`, `REFERENCE.md`, `DECISIONS.md`, `UI_Decisions.md`, `pyproject.toml`

**Changes**:
- Replaced top-level tabs with query-param-backed segmented navigation so History preview links stay on the History page.
- Changed History Gallery / Records into separate redraw views rather than concurrently rendered internal tab bodies.
- Kept selected History previews inline and visible in Gallery.
- Backfilled missing video thumbnails from existing local output files when ffmpeg is available, then re-queried History.
- Confirmed newest-first History ordering through `ORDER BY timestamp DESC, id DESC`.
- Added native Streamlit card actions for thumbnail preview, local downloads, and opening local files in the desktop file finder.

**Benefit**: A completed prediction remains easy to see, and History behaves like a visual browser first while keeping Records available as a separate table view.

---

## Verification

- `python -m compileall -q app.py src`
- `uv run ruff check .`
- Streamlit AppTest render with existing History rows: no app exceptions.
- Existing local video rows were backfilled with ffmpeg thumbnails where possible.
- Browser QA confirmed `?page=history` opens History directly and Gallery/Records render as separate views.
- No paid provider predictions were created.

### Final hardening notes

- The generation panel now uses an always-visible inline loading/result area instead of a collapsible `st.status` widget.
- History filters are rendered once and shared by Gallery and Records, avoiding duplicate Streamlit widget IDs.
- Video thumbnail creation is reusable for new downloads and for existing local video rows that predate the thumbnail pass.

---

## Notes

- The next planned milestone is v0.6.0: safety, metadata audit, dry-run payloads, and schema drift checks, followed by v0.6.5 verified Replicate 3D/texture model expansion.
- v0.x remains Replicate-only by design.
