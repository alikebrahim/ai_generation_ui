# UI Assessment — Pre-v1.0.0

**Project**: AI Generation Studio (`app.py` + `src/ui/`)  
**Assessed**: 2026-06-05  
**Current version**: v0.8.0  
**Purpose**: Inventory current interface elements, describe where they sit on each page, and give an honest opinion on what is sane vs what should change before declaring v1.0.0.

**Guidance note (exclusions)**: Example prompts, starter examples, lyrics/script starters, and any related suggestions for adding example content or "nice-to-have" prompt helpers are excluded from consideration in this document per direction. All references have been removed. Ignore this aspect entirely; it is marked for removal and should not influence UI element or component recommendations.

This version of the assessment incorporates a detailed code review of the current `src/ui/*.py` implementation plus the original document. It emphasizes practical readjustments to existing elements (column usage, render ordering, model selector location, section names, History hierarchy, widget choice for filters, preview styling) over adding new UI surfaces.

This assessment is based on a full read of the UI modules (`src/ui/*.py`, `app.py`, `UI_Decisions.md`). It does not replace hands-on browser QA on your machine (screen size, dark mode, long forms, real uploads).

---

## Executive summary

The app already follows a **coherent creative-workflow pattern**: pick a task → pick a model → fill inputs → tune settings → generate → watch the left preview panel → find past work in History. That matches the v0.5 design intent in `UI_Decisions.md` and is a solid base for a personal tool.

What holds v1.0 back is less “missing features” and more **consistency, ordering, and cognitive load** across UI elements and components:

| Area | Verdict |
|------|---------|
| Overall layout (preview left, controls right) | **Good** — familiar and keeps results visible |
| Plain-English labels & advanced collapse | **Good** on video/3D; audio is simpler and clearer; section names could still be friendlier |
| Prompt / media ordering vs preview pane | **Needs work** — creative inputs often appear below the empty result area |
| Cross-tab consistency (model placement, preview styling, workflow widgets) | **Needs work** — three tabs do not feel like one product |
| History page information order | **Needs work** — stats and per-model breakdown sit above filters/gallery |
| “Copy” actions in History | **Misleading** — shows text in the page, not clipboard copy |
| Developer/debug surfaces in the main path | **Borderline** — schema diagnostics and raw JSON are visible to everyone |
| Mobile / narrow viewport | **Unknown risk** — many horizontal radios and a narrow control column |

**Recommendation before v1.0**: one focused **UI element & component readjustment pass** rather than new features. Unify model card + prompt ordering + preview styling, reorder History, rename jargon sections, switch workflow filters to segmented controls, and tighten vertical space. This will make the product feel coherent without a redesign. The existing assessment of “no full redesign required” still holds.

---

## Method

- Mapped every major Streamlit widget group in `app.py` and tab modules.
- Compared implementation to `UI_Decisions.md` (v0.5 target) and `AGENTS.md` plain-English UX goals.
- Noted intentional deferrals already in `ROADMAP.md` (e.g. Aleph keyframes).

---

## Global shell (`app.py` + `src/ui/style.py`)

### Elements (top to bottom)

| Element | Placement | Role |
|---------|-----------|------|
| Page config | App init | Wide layout, title “AI Generation Studio”, 🎬 icon |
| Injected CSS | Global | Padding, full-width buttons, gallery thumb styling, **red-bordered preview panel** on video/3D |
| Token check | Before nav | Hard stop with `st.error` if `REPLICATE_API_TOKEN` missing |
| `st.title` + caption | Top of main column | Branding + one-line purpose |
| `st.divider` | Below title | Visual break |
| **Segmented control** | Below divider | Main nav: Video \| 3D \| Audio \| History (`?page=` query param) |

### Opinions

- **Segmented nav** is the right call (per `UI_Decisions.md`): deep links and History preview survive reruns better than `st.tabs`.
- **Double header stack** (app title + tab `st.header`) uses vertical space. Acceptable for desktop; on a laptop with browser chrome + Streamlit toolbar, the first screenful is mostly chrome before workflow controls.
- **No sidebar** keeps the mental model simple; everything competes in one column — fine for personal use, but the right control column becomes the bottleneck on smaller widths.
- **Emoji in nav labels** (🎥 🧊 🎵 📊) helps quick scanning for mixed technical comfort; slightly informal, which fits a household personal app.

---

## Shared generation layout (`forms.py`, `audio_forms.py`, `generation_panel.py`)

### Dominant pattern (Video & 3D; Audio similar)

```
[ Tab header + caption ]
[ Workflow filter — horizontal radio ]
[ Divider ]
[ Model block — placement varies by tab ]
[ Subheader: "Generate with {display_name}" ]
┌─────────────────────────────┬──────────────────┐
│  LEFT (~2.2)                │  RIGHT (~1.3)    │
│  Bordered preview panel     │  Bordered        │
│  - Status / progress        │  controls box:   │
│  - Result (video/3D/audio)  │  - Presets (if)  │
│  - Sometimes media uploads  │  - Balanced      │
│    (motion/edit/multimodal) │  - Cost caption  │
│                             │  - Advanced ▼    │
│                             │  - Preview req ▼ │
│                             │  - Generate btn  │
└─────────────────────────────┴──────────────────┘
[ Prompt / image sections — often FULL WIDTH below the 2-col row ]
```

### Preview panel (`generation_panel.py` + CSS)

- Left panel shows idle message, then live status, progress line, and final result.
- CSS highlights the preview container (red border) when it contains `.ai-prediction-preview-anchor` — **video and 3D use this; audio does not**, so Audio feels visually flatter.
- **Opinion**: The left panel is the best UX decision in the app. Users always know where to look during a long Replicate job. Extending the same anchor styling to Audio would unify the three tabs.

### Controls column

- **Balanced controls** always visible; **Advanced controls** collapsed by default — aligns with “leave this alone unless…” guidance.
- **Estimated cost** appears as a caption before Generate — honest and well placed.
- **Generate** is primary, full width in the narrow column — good affordance, but on wide monitors the button is far from the prompt (which may sit below the two columns).
- The 2.2 / 1.3 column ratio and late placement of prompt/media (after the columns in render order) are the biggest visual/functional friction points. Prompt and primary subject/start images render full-width *below* the preview + controls row. This puts the main creative input physically after the (empty) result pane and makes the right column the only place the Generate button can live, creating back-and-forth eye movement and unnecessary scrolling on complex forms.

### Request preview (`request_preview.py`)

- Collapsed expander: “Preview request (no charge)” → “Update preview” → summary, optional endpoint line, **Schema diagnostics (developer)**, full JSON payload.
- **Opinion**: Valuable for you debugging payloads; confusing for a non-technical user who might open it and think something is wrong. For v1.0, either move diagnostics behind a single “Developer tools” expander at the bottom of the tab, or hide when an env flag is off.

### Visual & component readjustment opportunities (shared)

- **Prompt / primary media placement**: Reorder or restructure render so the text prompt (and optional image upload when relevant) appear *before* or *integrated with* the preview/controls split. Preferred pattern: main creative inputs (prompt + key media) at the top of the workspace or stacked inside the wider left column above the live preview area; parameter controls stay in the right column. This restores a top-to-bottom “decide what → tune how → generate → watch result” flow without the result pane appearing before the user has written anything.
- **Left-column focus**: For normal (non-archetype) cases, move render of prompt + subject/start image into the preview column (above the anchor + result renderer). Right column becomes purely settings + cost + advanced + generate. Special wide media (motion/edit) already live in left — this would make the pattern consistent.
- **Column ratio**: 2.2:1.3 favors preview but starves the controls for rich models (many sliders + file uploads). Consider 1.8:1.7 or 2:1.5, or make the split adjustable / responsive via CSS for the right column to breathe.
- **"Balanced / Advanced" naming**: Technical. Rename section to “Main settings” (or “Common settings”) and expander to “More settings (optional)” or “Advanced (optional)” to better match the plain-English goal in AGENTS.md.
- **Workflow filters**: 6 horizontal radio options on Video wrap or squeeze easily. Consider switching to `st.segmented_control` (already used for global nav) for a chip-like, more scannable, consistent selection UI.
- **Audio preview parity**: Audio’s preview column lacks the `.ai-prediction-preview-anchor` span and therefore the red border styling that unifies Video/3D. Add the anchor (and update any audio-specific idle messaging) so all three generation experiences feel like one product.

---

## Video tab (`video_tab.py`, `video_workflow.py`, `forms.py`)

### Element inventory & placement

| Step | Element | Placement |
|------|---------|-----------|
| 1 | `st.header` “Video Generation” + caption | Top |
| 2 | Workflow radio (6 options, horizontal) | Under header — “What do you want to do?” |
| 3 | Model bordered box | After `st.divider` — `#### Model` + selectbox + optional caption |
| 4 | `Generate with {name}` subheader | Start of form |
| 5 | Preview + controls columns | Core workspace |
| 6 | Text prompt / image prompts | **Below** the 2-column row (side-by-side if both needed) |
| 7 | Multimodal / motion / edit media | In preview column (wide) or dedicated sections |
| 8 | Presets + Apply / Reset | Top of right controls box (rich models only) |
| 9 | Balanced + Advanced + Preview request + Generate Video | Right column |

### Strengths

- Workflow-first filtering (text / animate / motion / edit / multimodal) reduces “which of 11 models?” paralysis.
- Archetype-specific layouts (motion transfer, Aleph-style edit, Seedance multimodal frames) put **media next to preview** where it matters.
- Remix from History integrates via toast + session prefill.

### Issues / opinions

1. **Prompt and primary media sit below the 2-column workspace** (see shared layout section) — the core visual and flow problem. User sees empty preview pane first, must scroll past it to enter the prompt that will populate that pane, then look back up/right for Generate.
2. **Six horizontal workflow radios** will wrap or squeeze on narrow windows; labels like “Multimodal / references” are long. Switching to segmented_control would improve scanability and consistency with the main nav.
3. **Right column (~37% width)** stacks many sliders for rich models (Seedance, Kling) — lots of scrolling in a thin strip while the left panel is mostly empty until generation runs. Ratio and/or prompt placement changes would help.
4. **Inconsistent with 3D/Audio** model placement (see below) — same app, three different “where is the model?” stories.

---

## 3D tab (`threed_tab.py`, `forms.py`)

### Element inventory & placement

| Step | Element | Placement |
|------|---------|-----------|
| 1 | Header + caption | Top |
| 2 | Workflow radio (5 options) | Horizontal |
| 3 | Optional model caption | **Above divider** (output/pricing notes) |
| 4 | Divider | |
| 5 | Preview + controls columns | |
| 6 | **Model selectbox** | **Inside right controls box** (via `model_selector_renderer`) |
| 7 | Prompt / image / mesh upload sections | Full width below columns (mode-dependent) |
| 8 | `use_spinner` on generate | Extra spinner message vs video |

### Strengths

- 3D workflow filter (image / text / multiview / texturing) matches how users think about the task.
- Per-model captions (`_threed_model_caption`) are plain English and helpful.
- Hunyuan multiview and mesh upload paths are grouped in bordered sections.

### Issues / opinions

1. **Model picker rendered inside the form / right area** (via callback) while Video and Audio use a consistent top bordered “#### Model” card before the workspace — the primary cross-tab inconsistency. Fix by moving the selector out to match the other tabs.
2. **Pricing/output caption above divider** can duplicate text that also appears under the model selector — minor noise.
3. **3D preview in left panel** uses `<model-viewer>` only after success; until then the left panel is tall empty bordered space — same as video, but 3D jobs are slower (7 min hint), so the empty panel stares longer. The shared prompt-below-columns problem also affects 3D (subject image + optional prompt live below the empty preview).

---

## Audio tab (`audio_tab.py`, `audio_forms.py`)

### Element inventory & placement

| Step | Element | Placement |
|------|---------|-----------|
| 1 | Header + caption | Top |
| 2 | Workflow radio (All / Make music / Generate speech) | Horizontal |
| 3 | Divider | |
| 4 | Model bordered box | Selectbox + category caption (Music/Speech) |
| 5 | Subheader + pricing caption | |
| 6 | Preview + controls | Same 2.2 / 1.3 split |
| 7 | Main input (`lyrics` / `text` / `prompt`) | Right column only |
| 8 | Settings + Advanced + cost + preview + Generate Audio | Right column |

### Strengths

- Simplest tab — appropriate for music/speech (fewer file uploads).
- Workflow split (music vs speech) is clear for non-technical users.
- Cost estimation adapts to text length / duration — good feedback before paying.

### Issues / opinions

1. **Model appears twice in spirit**: bordered “Model” block, then again `Generate with {name}` — redundant headers.
2. **No preview-panel CSS anchor** — visual parity with video/3D missing.
3. **All inputs in the narrow right column** — fine for text-only; if you add reference audio uploads later, the column will feel cramped fast.

---

## History tab (`history_tab.py`)

### Element inventory & placement (actual order)

| Order | Element | Notes |
|-------|---------|-------|
| 1 | Header + caption | |
| 2 | Segmented control: Gallery \| Records | |
| 3 | **Three metrics** (total gens, cost, avg time) | Only if history non-empty |
| 4 | **“By Model”** subheader + one expander per model with cost/time metrics | Can be long with many models |
| 5 | *(Gallery path)* Filters: search, model, provider, status | **Below** stats |
| 6 | Inline gallery preview (if `?preview_generation_id=`) | |
| 7 | Gallery cards (up to 4 columns) OR Records dataframe | |
| 8 | “Load more history” | Gallery only |

### Gallery card (per item)

- Thumbnail or type icon, status emoji, model name, timestamp, prompt caption.
- Expander: “Copy actions” (prompt / JSON settings / seed) — **renders `st.code` after button click**, not clipboard API.
- Cost metric, local/temporary/missing indicators, download / open URL / file finder, **♻️ Load settings into tab (remix)**.

### Strengths

- Gallery-first matches v0.5 decisions; Records view is clearly for troubleshooting.
- Local vs temporary vs missing-local messaging is honest and useful.
- Inline preview with video / audio / model-viewer avoids leaving History.
- Remix to the correct tab (including audio) is a strong creative loop.

### Issues / opinions

1. **Information hierarchy is inverted for browsing**: users opening History to *find a clip* hit aggregate stats and per-model accounting first. Filters and gallery should come immediately after the Gallery/Records toggle (stats optional or collapsed below). Move the three metrics and the entire “By Model” subheader + expanders to a bottom “Usage stats” expander or after the visible gallery content.
2. **“Copy prompt” / “Copy settings” labels overpromise** — they show copyable blocks; users may think it failed. For v1.0, rename the expander to “View prompt & settings” and the buttons to “Show prompt”, “Show settings (JSON)”, etc. Real clipboard integration can be a follow-up if Streamlit exposes a reliable API in the target version.
3. **“Preview this thumbnail” button** under every thumb is redundant if the thumbnail itself should select preview (one click vs two). Make the image (or its container) the primary clickable target for preview; keep a subtle “Preview” affordance or caption hint rather than a full-width button on every card.
4. **Records table** exposes provider job IDs and raw URLs — correct for debugging, overwhelming for casual browsing (acceptable if Records is explicitly the power view).
5. **No type filter** (video / 3D / audio) in the filter row — only model multiselect; with 27 models, narrowing by media type would help. Add simple chips or a multiselect for Type alongside the existing model/provider/status filters.
6. **Gallery limit (24) + Load more** is fine technically; easy to miss that older items exist. Consider an “Older items available — load more” caption or infinite-scroll feel if easy.

---

## Cross-cutting inconsistencies (priority for v1.0 “sane UI”)

| # | Topic | Video | 3D | Audio |
|---|--------|-------|-----|-------|
| 1 | Where model is chosen | Top bordered card | Inside right / via renderer (between columns and prompt) | Top bordered card |
| 2 | Preview panel highlight (red border) | Yes (CSS + anchor) | Yes (CSS + anchor) | No (missing anchor) |
| 3 | Prompt/media vs preview order | Media/prompt **below** columns | Same (plus model selector in between) | N/A (text in right col) |
| 4 | Generate button label | Generate Video | Generate 3D Model | Generate Audio |
| 5 | Extra spinner on run | No | Yes | No |
| 6 | Workflow filter UI | Horizontal radio (6 options) | Horizontal radio | Horizontal radio |

These are not bugs — they are **product polish** issues that make the app feel like three apps stitched together. The biggest element/component readjustments needed are consistent model card placement, prompt-before-or-beside-preview ordering, preview styling parity, and History information order. Minor ones (naming, filter widget choice, column ratio, button density) are cheap wins for perceived quality.

---

## Alignment with `UI_Decisions.md`

| Decision | Status |
|----------|--------|
| Minimal creative tool, not API dashboard | **Mostly met** — except request preview JSON and schema diagnostics |
| Model → inputs → basic → advanced → generate → result | **Partially met** — result panel is visually *above* inputs on video/3D because prompt/media render after the columns; model placement also varies |
| Short copy; help in tooltips | **Met** — `param_help`, `friendly_label`, media roles |
| Segmented nav + query params | **Met** — Audio added (doc still says 3 destinations) |
| Generate never clipped | **Usually met** — depends on model param count + scrolling in right column |
| History gallery-first | **Met** — but stats block precedes gallery |
| Plain section names | **Mixed** — “Balanced controls” is jargon; “Main input” on audio is fine |

---

## Accessibility & household-user considerations

Assumptions from `AGENTS.md`: at least one user prefers plain language.

**Working well**

- Workflow radios use questions (“What do you want to do?” / “What kind of 3D?”).
- Media roles (“start frame”, “subject image”) on many models.
- Failure messages via `friendly_error_message` + optional technical expander on errors (better than exposing raw traces by default).

**Still rough**

- “Balanced controls” vs “Advanced controls” — consider **“Main settings”** (or “Common settings”) and **“More settings (optional)”** (see checklist).
- Star markers (★) on high-impact params help power users but need a one-line legend once per tab.
- Horizontal radio groups with no visible “selected” styling beyond Streamlit default — fine on desktop, easy to mis-tap on trackpad. (Switching workflows to segmented_control would help here too.)
- History card density: many buttons per card (copy expander, file finder, download, remix) — good power, busy for casual review. Group actions and make thumbnail the preview trigger.
- Prompt appearing below the preview pane on video/3D creates an inverted information scent for the primary creative task.

---

## Recommended v1.0 UI checklist (element & component readjustments)

Focus: make the three generation tabs feel like one product and fix the most common eye-flow / hierarchy complaints. These are targeted layout, naming, ordering, and styling changes rather than new features.

### Must-have (sanity / consistency pass)

1. **Unify generation tab layout & model placement**  
   Every tab must follow the exact same skeleton after the workflow filter:  
   - Bordered “#### Model” card (selectbox + caption/notes)  
   - Then the workspace (preview left / controls right)  
   - Prompt + primary media either above the split or stacked inside the left column above the result area (see readjustment notes).  
   Move the 3D model selector out of the renderer callback into the same top card pattern used by Video and Audio.

2. **Fix prompt / media ordering relative to preview**  
   Stop rendering the main text prompt and subject/start/reference images *after* the preview+controls columns. Either:  
   - Render prompt/media sections first (full width), then the split below, or (preferred for focus)  
   - Render key inputs inside the left (wider) column, above the prediction anchor and result.  
   This eliminates the “see empty result before you have written the prompt” problem.

3. **Give Audio the same preview visual treatment**  
   Inject the `.ai-prediction-preview-anchor` (and any needed idle state) inside Audio’s left column container so the red border / highlight styling applies. Audio must not feel like the “flat” tab.

4. **History: filters + gallery first, stats last**  
   After the Gallery/Records segmented control: immediately render the filters (search + model + provider + status + new Type filter), then the gallery or records content.  
   Move the three top metrics and the entire “By Model” accounting block to a collapsed “Usage stats” expander at the bottom of the History page (or after “Load more”).

5. **Rename/fix Copy actions + improve thumbnail click target**  
   Change the expander title from “📋 Copy actions” to “View prompt & settings”.  
   Button labels become “Show prompt”, “Show settings (JSON)”, etc. (the current behavior of revealing a code block + toast is acceptable; real clipboard is nice-to-have).  
   Make the thumbnail image itself (or a clearly indicated card area) the primary way to open the inline preview; de-emphasize or remove the separate full-width “Preview this thumbnail” button.

6. **Gate or clearly label developer surfaces**  
   Keep the request preview expander but consider renaming to “Inspect payload (advanced)” or similar. Ensure schema diagnostics stay nested under their own “Developer diagnostics” expander. Do not let raw JSON be the first thing a household user sees when they open the expander.

7. **Add Type filter on History**  
   Video / 3D / Audio (as chips or multiselect) so users can quickly narrow the gallery without scrolling a 27-item model list.

### Component polish (cheap visual/functional wins)

- Rename “Balanced controls” heading to “Main settings” (or “Common settings”) and the Advanced expander to “More settings (optional)”.
- Switch workflow filter radios to `st.segmented_control` (matches global nav styling, feels more modern and tappable).
- Add a one-line legend near the first ★ high-impact param on each tab: “★ = large effect on quality, time or cost”.
- Tighten or conditionally reduce the global title + caption + divider chrome so the workflow + model + prompt area is visible in the first screenful on a typical laptop.
- Experiment with column ratios (try 1.8:1.7 or 2:1.5) and/or allow the right column more breathing room when many balanced + file params are present.
- Reduce per-card action density in History: put the most common actions (remix, download if local, open) in a compact row; move file-finder / large downloads into a “⋯ More” or keep only the essentials prominent.
- Consider softening the preview border color or adding a stronger “this is where your result will appear” idle state message while keeping the visual anchor.

### Nice-to-have (still pre-1.0 if cheap)

- Click thumbnail → preview (largely covered by #5 above).
- Reduce top vertical chrome (merge app caption into tab header or shorten).
- Aleph keyframes remain post-1.0 per roadmap — do not block v1.0.

### Explicitly out of scope for “sane UI” v1.0

- Full redesign / custom theme / sidebar nav.
- Side-by-side model comparison (roadmap post-1.0).
- Dynamic OpenAPI-driven forms (roadmap exploration).
- Adding any example prompts or starters (explicitly excluded — see top guidance).

---

## Overall opinion

The interface is **already usable and thoughtfully engineered** for a Replicate-backed personal studio: workflow filters, dry-run preview, persistent History, remix, and a dedicated preview column are the right pillars. The left-anchored result panel is one of the strongest UX decisions — it respects that generations take time and the user should not lose context.

It does **not** yet feel like a single polished product for two main reasons:

1. **Element & component placement is inconsistent** across the three generation tabs (model card location, prompt ordering vs. preview, preview styling, workflow widget choice, spinner behavior).
2. **Information hierarchy is inverted in History** (accounting before browsing) and on the generation pages (empty preview pane appears before the prompt that will fill it).

The user’s instinct is correct: the UI elements and components would benefit from a deliberate readjustment pass more than from adding new affordances. The fixes are mostly reordering render calls, extracting the model selector into a shared helper, injecting one CSS anchor, renaming a couple of headings, reordering History sections, and small widget swaps. None of this requires a theme rewrite or new architecture.

For v1.0.0, “sane UI” should mean: **a non-technical user can open any tab, immediately understand where to pick the model and type the prompt, watch the result appear in the same prominent left area, then find and remix prior work in History without first wading through stats or guessing which button copies vs. shows.** A focused consistency + ordering pass (checklist above) will achieve that.

Hands-on validation on your target screen (resolution, browser, dark/light) remains the final gate; this document is the map for what to look at when you click through. After the readjustments, re-capture a few key screenshots (default T2V, I2V with image, text-to-3D, music, History gallery with filters) to confirm the flow feels linear.

**Implementation note (2026 follow-up)**: All must-have checklist items + core component polish (model unification, prompt ordering into left column, audio anchor, History reorder + Type filter, segmented workflows, renames, examples removal, chrome, labels, legend, compact actions) have been implemented and pass compile/ruff. See git diff for the exact edits. Manual Streamlit QA by user recommended next (no paid generations used in the pass).

---

## Source files referenced

| File | Responsibility |
|------|----------------|
| `app.py` | Shell, navigation, tab dispatch |
| `src/ui/style.py` | Global CSS |
| `src/ui/video_tab.py` | Video tab orchestration |
| `src/ui/video_workflow.py` | Video workflow filter + archetype media |
| `src/ui/threed_tab.py` | 3D tab orchestration |
| `src/ui/audio_tab.py` | Audio tab orchestration |
| `src/ui/forms.py` | Shared video/3D form layout |
| `src/ui/audio_forms.py` | Audio form layout |
| `src/ui/generation_panel.py` | Preview panel + generation run UI |
| `src/ui/result_views.py` | Success/failure result rendering |
| `src/ui/request_preview.py` | Dry-run expander |
| `src/ui/history_tab.py` | History gallery + records |
| `UI_Decisions.md` | v0.5 target UX (partially stale on Audio) |