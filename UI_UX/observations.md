# UI/UX Visual QA Notes

Target: http://localhost:8501
Mode: Hermes browser tools connected to visible Chromium-family CDP browser via `/browser connect`.
Scope: visual/navigation/validation robustness pass; no paid generation submitted unless explicitly triggered later.


## Initial Video tab
- Browser tools are now attached via CDP (`stealth_features: cdp_override`), so this is the visible debug browser path.
- Console after navigation: 0 messages, 0 JS errors.
- Layout is clean and spacious: large title, clear Video / 3D / History tabs, model selector, then generation form.
- Video form has understandable grouping: prompt, “Text-only model” hint, “Balanced controls”, duration/resolution/aspect ratio/seed, cost estimate, advanced controls below the fold.
- Immediate UX note: the Generate Video button sits below the visible fold at this viewport; the user must scroll to see/use it. This is okay but could be improved by reducing top whitespace or keeping primary action closer to visible controls.
- Label issue from accessibility tree: some `LabelText` entries appear blank around select widgets, though visible labels are present. Worth checking Streamlit accessibility/aria labeling if this matters.

## Video tab interactions
- Model dropdown opens correctly and lists: Wan 2.7 T2V, Wan 2.5 I2V Fast, Seedance 2.0.
- UX note: model names are technically accurate but not especially explanatory for non-technical users. Consider adding short descriptions/subtext later, e.g. “Text only”, “Start image + text”, “Supports image/reference inputs/audio”.
- Switching from Wan 2.7 T2V to Wan 2.5 I2V Fast reset the prompt. That may be technically expected because forms rerender per model, but it can surprise users if they switch models after drafting a prompt.
- I2V form shows Prompt and Upload Image side-by-side. The upload control works visually, but “Upload Image” is generic; project guidance prefers role-specific wording like “start frame” where applicable.
- Non-paid validation worked for I2V:
  - Empty prompt + no image → alert: “Please enter a prompt.”
  - Prompt entered + no image → alert: “Please upload an image.”
- Console remained clean during these interactions: 0 JS errors observed.

## 3D tab
- Navigation to 3D works after a fresh reload; before reload, clicking 3D/History from an I2V validation state appeared not to switch tabs. This may be a tooling/ref focus issue, but it is worth re-checking manually because the visible page did not change on repeated tab clicks until reload.
- Hunyuan3D 2.0 default view is clear that current 3D models are Image-to-3D and has a plain-English blue info callout: "This model uses image input only (no text prompt)."
- Upload label is good: "Subject image" is clearer than generic "Upload Image".
- Clicking Generate 3D Model without a subject image did not visibly show an error in the captured viewport; the snapshot also did not show an error. This may be because the click target/scroll state was awkward, but it deserves follow-up: missing required subject image should produce an obvious inline validation message like the I2V path does.
- Hunyuan 3D 3.1 combined text/image UI is understandable: it says provide a text description or upload a subject image, not both.
- Hunyuan 3D 3.1 placeholder is helpful: "Describe what you want Hunyuan 3D 3.1 to generate..."
- Face Count is still technical. For non-technical users, help text should explain that higher face count can preserve detail but may cost/time/render more.
- Cost messaging for 3D says "Cost shown after generation". Honest, but less helpful before a paid call than video estimates.

## History tab
- Summary metrics render correctly: 4 total generations, $3.50 total cost, 3.4m average predict time.
- By Model groups are clean and collapsible.
- Model filter appears pre-populated with both available model chips. This makes it look like an active filter even though it is effectively "all". Consider clearer copy such as "All models" or no chips by default.
- Search prompt field shows placeholder examples and requires Enter to apply. This is consistent with Streamlit, but users may not realize filtering has not applied until Enter is pressed.
- Searching for "robot" filtered all visible generations away, but no empty-state message appeared under Gallery. This is a UX issue: show something like "No generations match this search." Otherwise the page looks like it failed to load.
- History cards show "Temporary link" clearly, which is good for expired Replicate URL expectations.
- Prompt text appears as "None" for existing history rows, which looks confusing/non-human. If the prompt was missing from legacy rows, display "No prompt recorded" or hide that line.

## Console / runtime
- Browser console reported no JS errors during this pass.
- No paid provider generation was submitted in this pass. Tests were navigation, visual inspection, model switching, and invalid-input validation only.
