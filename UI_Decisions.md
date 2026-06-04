# UI Decisions for v0.5.0-v0.5.10

Purpose: define the agreed UI direction for the v0.5.x patch series before implementation begins.

Scope: visual feel, layout, tabs, buttons, parameters, sections/components, generation display, model input patterns, History cards, thumbnails/previews, and result handling.

Non-goal: rename model names. Model names remain as currently displayed.

Related QA artifacts:
- `UI_UX/test_plan.md`
- `UI_UX/observations.md`
- `UI_UX/screenshots/`

---

## 1. General UI feel

Decision: the app should feel like a minimal creative generation interface, not an API dashboard.

The UI should follow the familiar flow used by hosted generation tools:

1. choose a model;
2. provide prompt/media inputs;
3. adjust common controls;
4. optionally open `Advanced controls`;
5. click Generate;
6. watch progress;
7. view the result;
8. find prior generations in History.

Visible copy should be short. Explanations should live in tooltips, short subtexts where needed, validation messages, or documentation, not as long paragraphs in the main UI.

Implication:
- Avoid instructional blocks unless the user is blocked without them.
- Prefer clear labels over explanatory sentences.
- Prefer simple section/control names: `Prompt`, `Start frame`, `End frame`, `Subject image`, `Basic controls`, `Advanced controls`, `History`.
- Keep the UI intuitive for users already familiar with other generation providers.

---

## 2. Minimal styling and visual layout

Decision: use light visual styling to make the app more pleasant while keeping it recognizably simple Streamlit.

Use lightweight containers, spacing, and minimal CSS only where it improves clarity. Avoid heavy custom theming.

Recommended generation-tab structure:

1. Page heading
2. Model selector
3. Input section
4. Basic controls
5. Cost/status note
6. Advanced controls
7. Generate button
8. Generation/result panel

Implication:
- Use `st.container(border=True)` or equivalent light grouping where useful.
- Keep the page clean and predictable, not crowded or heavily styled.
- The Generate button must never be clipped at the bottom of the viewport.
- Prefer small spacing/layout changes over decorative elements.

---

## 3. Top-level navigation

Decision: keep the same three top-level destinations — `Video`, `3D`, and `History` — but use query-param-backed segmented navigation instead of top-level `st.tabs`.

The navigation should feel polished and easy to scan, without turning the app into a custom frontend. Query params are preferred because History preview selections and direct links such as `?page=history` must remain on the correct page after Streamlit reruns.

Implication:
- Keep the same three top-level destinations: `Video`, `3D`, `History`.
- Use minimal styling around the header/navigation area.
- Preserve simple icon labels and active-page clarity.
- Avoid nested top-level navigation layers.

Implementation note:
- Streamlit `st.tabs` renders all tab bodies and can reset preview/deep-link behavior on rerun; use segmented controls plus query params for page-level navigation.

---

## 4. Buttons and primary actions

Decision: buttons should be minimal, obvious, and action-oriented.

Primary generation buttons remain direct:
- `Generate Video`
- `Generate 3D Model`

Decision: keep Generate after `Advanced controls`.

Generation form order:

`Basic controls → cost note → Advanced controls → Generate`

Implication:
- This preserves the current mental model: all controls are available before submission.
- The default path remains simple because `Advanced controls` stays collapsed.
- The Generate button must have enough bottom spacing and must be fully clickable.
- Download/open actions should appear only when relevant.

---

## 5. Parameters and controls

Decision: expose parameters without over-explaining them.

Common settings stay visible. Less common settings stay under `Advanced controls`.

Preferred visible labels:
- `Duration`
- `Resolution`
- `Aspect ratio`
- `Seed`
- `Generate type`
- `Face count`
- `Advanced controls`

Decision: parameter explanations should be mostly tooltips.

Implication:
- Do not add long visible descriptions below every control.
- Keep advanced controls collapsed by default.
- Use short visible subtext only when a control is risky, ambiguous, or likely to cause paid mistakes.
- Use friendly labels where possible, but do not hide technical values if they are necessary.

---

## 6. Prompt input behavior

Decision: do not add extra visible prompt instructions by default.

Decision: keep current Streamlit prompt behavior unless it becomes a real issue.

Implication:
- Avoid visible instructions like “When you click Generate, the current text here will be used” unless QA shows users need it.
- Keep prompt placeholder text concise.
- `st.form` can be explored later if prompt submission state becomes unreliable or confusing, but it is not part of the initial v0.5.0 plan.

---

## 7. Generation progress and result display

Decision: generation should happen in one focused inline panel.

When a user clicks Generate, the app should show a focused panel. That panel shows progress while running. When complete, the same panel displays the result. If generation fails, the same panel displays the failure message and prediction details.

Decision: use an inline panel, not a modal/dialog, for the first implementation.

Decision: completed results remain visible until replaced by the next generation.

Decision: no separate “generation succeeded” banner is required. The result replacing the loading state is the success state.

Keep existing useful prediction details:
- status;
- elapsed time;
- prediction ID;
- prediction URL/details when relevant;
- error message on failure.

Implication:
- Remove or de-emphasize redundant success toasts/banners if they create clutter.
- Keep failure messaging visible and specific.
- Avoid scattering status, success, and result into separate UI areas.
- Preserve the current progress/prediction detail style, but place it inside the focused panel.

---

## 8. Result components

Decision: results should be shown as the natural completion state of generation.

For videos:
- show playable preview when possible;
- show open/download action;
- show local-vs-temporary availability clearly but briefly.

For 3D:
- show model viewer/open/download action when possible;
- show preview/placeholder when model viewing is unavailable;
- show local-vs-temporary availability clearly but briefly.

Decision: keep separate video and 3D renderers, but share asset/status helper functions.

Implication:
- Video and 3D outputs need different UI treatments, so a single generic renderer could become awkward.
- Shared helpers should still avoid duplication for local/temporary status, download/open actions, and `OutputAsset` metadata handling.
- The result component should not require the user to open History to access the newly generated output.
- Failed local downloads must still preserve provider URL access.

---

## 9. Model input modes

Decision: models with multiple input modes should use explicit mode selection.

For Hunyuan 3D 3.1, the UI should ask for the mode first and show the relevant input, rather than showing prompt and subject image together with a paragraph explaining “not both.”

Decision: Hunyuan 3D 3.1 mode labels should be:
- `Create from text`
- `Create from image`

For future video models, possible modes include:
- `Text`
- `Start frame`
- `Start + end frame`
- `Reference image`

Implication:
- Prevents invalid prompt+image combinations before validation.
- Keeps the form smaller and easier to scan.
- Requires model/input metadata to drive conditional form rendering.

---

## 10. Media input roles

Decision: media uploads should be labeled by role.

Use role-specific labels:
- `Start frame`
- `End frame`
- `Subject image`
- `Reference image`

Avoid generic labels like `Upload Image` when the image role is known.

Decision: for start/end frame models, show start frame as the visible upload and hide end frame behind an optional control.

Decision: prompt remains visible for start/end frame models.

Implication:
- Model config should include media input role metadata instead of relying on one-off UI branches.
- Form rendering should use that metadata for labels, help text, and validation.
- This prepares the app for models with start/end frame inputs.
- Prompt remains part of the main creative direction even when media frames are provided.

---

## 11. Cost display

Decision: cost display should be concise.

If an estimate is available, show it. If not, keep:

`Cost shown after generation`

Implication:
- Cost messaging stays visible but not distracting.
- Detailed pricing explanations can live in tooltip/subtext if needed.
- Do not invent rough cost buckets unless pricing confidence is high.

---

## 12. History direction

Decision: History should become gallery-first.

Decision: History should have two separate redraw views:
- `Gallery`
- `Records`

`Gallery` is the default visual browsing view. `Records` is the table/detail view. These are selected with a segmented control and only one body renders at a time; they should not behave as nested/concurrent tab content.

Decision: show all history cards, with pagination or lazy loading added when needed.

Cards should include:
- thumbnail/preview;
- model name;
- short prompt or fallback text;
- date/time;
- cost/time when available;
- local/temporary/missing status;
- preview action;
- open/download action.

Implication:
- History needs reliable thumbnail/preview handling.
- Existing `None` prompt display should become a friendly fallback.
- Empty search/filter states need clear minimal messages.
- Detailed records stay available without dominating the default experience.
- A selected Gallery item should preview inline on History, and direct preview links should not reset the app to another page.

---

## 13. Video thumbnails

Decision: video History cards should use thumbnails/previews.

Decision: use `ffmpeg` for thumbnail extraction when available.

Decision: use the first frame as the thumbnail.

Preferred behavior:
- after a successful local video download, extract a first-frame thumbnail;
- store it in `outputs/thumbnails/`;
- persist `thumbnail_path` in History;
- show thumbnail on History card;
- fall back gracefully if extraction fails or `ffmpeg` is missing.

Implication:
- `ffmpeg` should be treated as an optional runtime capability, not as a hard app startup requirement.
- Thumbnail generation must not break generation success.
- If no thumbnail exists, cards should still render with a clean placeholder.

---

## 14. 3D previews and multi-asset downloads

Decision: 3D History cards should use static/preview assets in cards, with interactive viewing in result/detail view.

Preview order:
1. provider preview image/video if returned;
2. local preview asset if generated/stored;
3. placeholder card if no preview exists.

Decision: if a 3D model returns multiple assets, all useful assets should be downloaded when possible and linked to the same generation/prediction in History.

Implication:
- 3D output normalization must capture more than just one model URL when providers return model + preview + auxiliary files.
- History must preserve the relationship between all output assets and the same generation row.
- The user should be able to open/download the relevant resources from the same History card/detail area.
- Full local 3D thumbnail rendering can be deferred unless provider previews are insufficient.

Note:
- The v0.4.7/v0.4.8 architecture added `OutputAsset` and `output_assets_json`; v0.5.x should use this to ensure multi-asset downloads are represented consistently.

---

## 15. Validation and failures

Decision: validation and failure messages should be direct and minimal.

Use clear messages only when the user must act or when a generation fails.

Examples:
- `Please enter a prompt.`
- `Please upload a start frame.`
- `Generation failed.` followed by existing error/prediction details.

Implication:
- Avoid success banners.
- Keep failure details in the generation panel.
- Keep validation close to the control/action that caused it.

---

## 16. Proposed v0.5.x patch sequence

This sequence is the planned v0.5.x UI/UX roadmap before implementation.

### v0.5.0 — Minimal UI shell, layout reliability, and nicer tabs

Goals:
- Fix clipped Generate buttons and bottom spacing.
- Add minimal styling for a more pleasant tab/header presentation.
- Add light form/section containers where useful.
- Keep visible copy minimal.
- Keep parameter explanations mostly in tooltips.
- Keep Generate after `Advanced controls`.

Candidate files:
- `src/ui/forms.py`
- `src/ui/video_tab.py`
- `src/ui/threed_tab.py`
- `src/ui/history_tab.py`
- possible `src/ui/style.py`
- `app.py` if app-level style injection is needed

Verification:
- `python -m compileall -q app.py src`
- `uv run ruff check .`
- Visible browser QA: tabs look cleaner and every Generate button is fully visible/clickable.

### v0.5.1 — Focused generation panel for Video

Goals:
- Add focused inline generation panel for videos.
- Show existing progress/status/prediction details while running.
- Replace loading with video result on completion.
- Show failure message/details in the same panel.
- Remove/de-emphasize redundant success banners/toasts if they add clutter.

Candidate files:
- `src/ui/video_tab.py`
- `src/ui/result_views.py`
- possible `src/ui/generation_panel.py`

Verification:
- Dry-run/mock result rendering where possible.
- Paid generation only with explicit approval.

### v0.5.2 — Focused generation panel for 3D

Goals:
- Add focused inline generation panel for 3D.
- Show existing progress/status/prediction details while running.
- Replace loading with 3D result/open/download actions on completion.
- Show failure message/details in the same panel.

Candidate files:
- `src/ui/threed_tab.py`
- `src/ui/result_views.py`
- possible `src/ui/generation_panel.py`

Verification:
- Dry-run/mock result rendering where possible.
- Paid generation only with explicit approval.

### v0.5.3 — Hunyuan 3D 3.1 mode selector

Goals:
- Add `Create from text` / `Create from image` selector.
- Show only the relevant input.
- Prevent invalid text+image or neither-input states.

Candidate files:
- `src/ui/forms.py`
- possibly `src/models_config.py`

Verification:
- Text mode: prompt visible, image upload hidden.
- Image mode: image upload visible, prompt hidden.
- Empty selected mode is blocked clearly.

### v0.5.4 — Media role metadata and start/end frame pattern

Goals:
- Add model/config metadata for media roles.
- Render role-specific media labels.
- Start frame visible by default when supported.
- End frame hidden behind optional control when supported.
- Prompt remains visible for start/end-frame models.

Candidate files:
- `src/models_config.py`
- `src/domain.py`
- `src/ui/forms.py`

Verification:
- Seedance still uses start-frame language.
- Wan I2V uses role-specific label instead of generic upload wording.
- Start/end frame pattern can be represented in config.

### v0.5.5 — Video thumbnails for History cards

Goals:
- Extract/store first-frame video thumbnails after successful local downloads using `ffmpeg` when available.
- Show thumbnails on History gallery cards.
- Fall back cleanly when thumbnails are unavailable.

Candidate files:
- `src/storage_service.py`
- `src/history_service.py`
- `src/ui/history_tab.py`
- possible `src/thumbnail_service.py`

Verification:
- New local video can produce a thumbnail if `ffmpeg` is available.
- History card shows thumbnail or placeholder.
- Missing `ffmpeg` does not break generation or History.

### v0.5.6 — 3D previews and multi-asset History

Goals:
- Capture provider preview assets when available.
- Ensure all useful assets from a 3D prediction are downloaded when possible.
- Link all assets to the same generation/prediction through History metadata.
- Show static/preview asset or placeholder in History cards.
- Keep interactive model viewing in result/detail view.

Candidate files:
- `src/threed_gen.py`
- `src/storage_service.py`
- `src/history_service.py`
- `src/ui/history_tab.py`
- output asset normalization module/file

Verification:
- 3D generation output preserves model and preview asset metadata when available.
- History card renders preview or placeholder.
- Multi-asset output remains associated with one generation row.

### v0.5.7 — History Gallery/Records split and copy polish

Goals:
- Add `Gallery` and `Records` views in History.
- Make Gallery the default visual browsing view.
- Keep table/details in Records.
- Replace `None` prompt with a fallback.
- Add empty search/filter states.
- Improve local/temporary/missing labels.

Candidate files:
- `src/ui/history_tab.py`
- possibly `src/history_service.py`

Verification:
- Gallery and Records tabs both work.
- Search with no results shows a clear empty state.
- No-prompt rows display friendly fallback text.

### v0.5.8 — Gallery-first History layout and pagination/lazy loading prep

Goals:
- Show all generation cards in Gallery.
- Add pagination/lazy loading if needed for performance.
- Keep filters and open/download actions available.
- Keep card layout visually scannable.

Candidate files:
- `src/ui/history_tab.py`

Verification:
- Recent and older generations are accessible.
- Filters still work.
- Download/open actions still work.

### v0.5.9 — Final UX hardening and docs alignment

Goals:
- Consistent spacing and sections/components across Video, 3D, and History.
- Review tab styling, button placement, parameter grouping, generation panels, and History cards.
- Visible browser QA for all major states.
- Update README/CHANGELOG/ROADMAP/version docs if declaring v0.5.x complete.

Candidate files:
- `src/ui/forms.py`
- `src/ui/video_tab.py`
- `src/ui/threed_tab.py`
- `src/ui/history_tab.py`
- docs as needed

Verification:
- `python -m compileall -q app.py src`
- `uv run ruff check .`
- Visible browser QA screenshots for each page/state.
- No paid provider predictions unless explicitly approved.


### v0.5.10 — History preview/layout hardening

Goals:
- Keep generation and History previews visible instead of collapsed.
- Make `Gallery` and `Records` redraw as separate History views.
- Keep preview selections on History using query-param-backed navigation.
- Backfill missing thumbnails from existing local video outputs when possible.
- Preserve newest-first gallery ordering.

Candidate files:
- `app.py`
- `src/ui/history_tab.py`
- docs as needed

Verification:
- `python -m compileall -q app.py src`
- `uv run ruff check .`
- Browser QA for `?page=history`, Gallery preview, Records view, and local thumbnail/card actions.
- No paid provider predictions unless explicitly approved.

---

## Remaining open questions

None required before starting v0.5.0.

Implementation may still discover technical trade-offs, especially around Streamlit styling hooks, `ffmpeg` availability, and provider-specific 3D multi-asset output shapes. If those trade-offs materially affect UX or scope, update this document before changing direction.
