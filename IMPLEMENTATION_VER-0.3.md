# v0.3.0 Implementation — Model Capability Matrix + Schema-Driven UX

> **For Hermes:** Use subagent-driven-development skill to implement each phase.
> Each task is bite-sized (2-5 min). TDD where possible. Commit after each task.

**Goal:** Prevent all known invalid Replicate API calls by adding per-model parameter
constraints, updating UI controls to show only schema-valid options, and adding
pre-submit validation. This combines the v0.2.1 Wan 2.7 T2V urgent fix with the
broader v0.3.0 capability matrix.

**Architecture:** Add a `param_constraints` dict to `ModelConfig` dataclass that
describes per-parameter valid ranges, enums, and UI control types. Update `app.py`'s
`_render_param_widget()` to consume these constraints, and add `_validate_params()`
to block invalid payloads before `replicate.predictions.create()`.

**Tech Stack:** Python 3.11+, Streamlit, Replicate client, dataclasses

**Live schema sources (verified 2026-06-03):**
All constraints below were extracted from Replicate's live OpenAPI schemas via the
Python client (`model.latest_version.openapi_schema`).

---

## Phase 1: Data Layer — Schema-Validated Parameter Constraints

### Task 1.1: Add `param_constraints` field to ModelConfig

**Objective:** Add a structured constraints field to the dataclass.

**Files:**
- Modify: `src/models_config.py`

**Implementation:**

Add a new `ParamConstraint` type and a `param_constraints` field to `ModelConfig`:

```python
from typing import TypedDict, NotRequired

class ParamConstraint(TypedDict, total=False):
    """Validated per-parameter constraint from live Replicate schema."""
    # For numeric params
    min: int | float
    max: int | float
    # For enum params — constrains both widget and validation
    enum: list[str]
    # UI control override — "slider", "dropdown", "number", "checkbox"
    ui_type: str
    # If the param supports null
    nullable: bool

@dataclass
class ModelConfig:
    # ... existing fields ...
    param_constraints: dict[str, ParamConstraint] = field(default_factory=dict)
```

**Step 5:** Commit: `feat: add param_constraints field to ModelConfig dataclass`

---

### Task 1.2: Add validated constraints for Wan 2.7 T2V

**Objective:** Add live-schema-verified constraints for `wan-video/wan-2.7-t2v`.

**Files:**
- Modify: `src/models_config.py` (WAN_2_7_T2V block)

**Implementation:**

```python
WAN_2_7_T2V = ModelConfig(
    # ... existing fields ...
    param_constraints={
        "duration": {"min": 2, "max": 15, "ui_type": "slider"},
        "resolution": {"enum": ["720p", "1080p"], "ui_type": "dropdown"},
        "aspect_ratio": {
            "enum": ["16:9", "9:16", "1:1", "4:3", "3:4"],
            "ui_type": "dropdown",
        },
        "seed": {"nullable": True},
    },
)
```

**Verification:** Default values (5s, 1080p, 16:9, seed=-1) are all within constraints.

**Step 5:** Commit: `feat: add live-schema constraints for Wan 2.7 T2V`

---

### Task 1.3: Add validated constraints for Wan 2.5 I2V Fast

**Objective:** Add live-schema-verified constraints. Duration is not a slider — only 5s or 10s.

**Files:**
- Modify: `src/models_config.py` (WAN_2_5_I2V block)

**Implementation:**

```python
WAN_2_5_I2V = ModelConfig(
    # ... existing fields ...
    param_constraints={
        "duration": {"enum": [5, 10], "ui_type": "dropdown"},
        "resolution": {"enum": ["720p", "1080p"], "ui_type": "dropdown"},
        "seed": {"nullable": True},
    },
)
```

**Note:** Duration is an enum in the live schema (only 5 or 10), not a slider.

**Step 5:** Commit: `feat: add live-schema constraints for Wan 2.5 I2V Fast`

---

### Task 1.4: Add validated constraints for Seedance 2.0

**Objective:** Add full constraints. Seedance has the richest parameter set.

**Files:**
- Modify: `src/models_config.py` (SEEDANCE_2_0 block)

**Implementation:**

```python
SEEDANCE_2_0 = ModelConfig(
    # ... existing fields ...
    param_constraints={
        "duration": {"min": -1, "max": 15, "ui_type": "slider"},
        "resolution": {"enum": ["480p", "720p", "1080p"], "ui_type": "dropdown"},
        "aspect_ratio": {
            "enum": ["16:9", "4:3", "1:1", "3:4", "9:16", "21:9", "9:21", "adaptive"],
            "ui_type": "dropdown",
        },
        "seed": {"nullable": True},
        "image": {"nullable": True},
    },
)
```

**Note:** Duration supports -1 for "intelligent duration" mode.

**Step 5:** Commit: `feat: add live-schema constraints for Seedance 2.0`

---

### Task 1.5: Add validated constraints for Hunyuan3D-2

**Objective:** Add constraints for the 3D model.

**Files:**
- Modify: `src/models_config.py` (HUNYUAN3D_2 block)

**Implementation:**

```python
HUNYUAN3D_2 = ModelConfig(
    # ... existing fields ...
    param_constraints={
        "steps": {"min": 20, "max": 50, "ui_type": "number"},
        "guidance_scale": {"min": 1.0, "max": 20.0, "ui_type": "number"},
        "octree_resolution": {"enum": [256, 384, 512], "ui_type": "dropdown"},
    },
)
```

**Step 5:** Commit: `feat: add live-schema constraints for Hunyuan3D-2`

---

### Task 1.6: Add validated constraints for TRELLIS 2 + fix pipeline_type

**Objective:** Add constraints AND fix the pipeline_type dropdown to match live schema.

**Files:**
- Modify: `src/models_config.py` (TRELLIS_2 block)

**Implementation:**

```python
TRELLIS_2 = ModelConfig(
    # ... existing fields replaced ...
    balanced_params=[
        "image",
        "seed",
        "pipeline_type",
    ],
    advanced_params=[
        "generate_model",
        "generate_video",
        "texture_size",
        "decimation_target",
        "preprocess_image",
        "sparse_structure_steps",
        "shape_slat_steps",
        "tex_slat_steps",
        "shape_slat_guidance_strength",
        "tex_slat_guidance_strength",
    ],
    defaults={
        "seed": 42,
        "pipeline_type": "1024_cascade",
        "generate_model": True,
        "generate_video": True,
        "texture_size": 4096,
        "decimation_target": 1_000_000,
        "preprocess_image": True,
        "sparse_structure_steps": 12,
        "shape_slat_steps": 12,
        "tex_slat_steps": 12,
        "shape_slat_guidance_strength": 7.5,
        "tex_slat_guidance_strength": 1.0,
    },
    param_constraints={
        "pipeline_type": {
            "enum": ["512", "1024", "1024_cascade", "1536_cascade"],
            "ui_type": "dropdown",
        },
        "texture_size": {"min": 1024, "max": 8192, "ui_type": "number"},
        "decimation_target": {"min": 100000, "max": 2000000, "ui_type": "number"},
        "sparse_structure_steps": {"min": 1, "max": 50, "ui_type": "number"},
        "shape_slat_steps": {"min": 1, "max": 50, "ui_type": "number"},
        "tex_slat_steps": {"min": 1, "max": 50, "ui_type": "number"},
        "shape_slat_guidance_strength": {"min": 0.0, "max": 15.0, "ui_type": "number"},
        "tex_slat_guidance_strength": {"min": 0.0, "max": 15.0, "ui_type": "number"},
    },
)
```

**Note:** pipeline_type enum changed from `['512_fast', '1024_cascade', '2048_quality']`
to `['512', '1024', '1024_cascade', '1536_cascade']` matching the live schema.

**Step 5:** Commit: `feat: add live-schema constraints for TRELLIS 2 + fix pipeline_type enum`

---

## Phase 2: UI Layer — Schema-Driven Controls

### Task 2.1: Update `_render_param_widget` to use model constraints

**Objective:** Rewrite the widget renderer to query `model.param_constraints` for
valid options, ranges, and UI type overrides.

**Files:**
- Modify: `src/models_config.py` (add helper functions)
- Modify: `app.py` (`_render_param_widget`)

**Implementation (new helper in models_config.py):**

```python
def get_options_for_param(model: ModelConfig, param_name: str) -> list[str] | None:
    """Return enum options if defined, else None (means use generic)."""
    c = model.param_constraints.get(param_name, {})
    return c.get("enum")

def get_range_for_param(model: ModelConfig, param_name: str) -> tuple[int | float | None, int | float | None]:
    """Return (min, max) for numeric params, or (None, None)."""
    c = model.param_constraints.get(param_name, {})
    return (c.get("min"), c.get("max"))

def is_param_nullable(model: ModelConfig, param_name: str) -> bool:
    """Return True if the parameter accepts null."""
    c = model.param_constraints.get(param_name, {})
    return c.get("nullable", False)
```

**Step 5:** Commit: `feat: add constraint query helpers to models_config`

---

### Task 2.2: Update duration widget to use model constraints

**Objective:** Duration should be a dropdown when enum, slider when range.

**Files:**
- Modify: `app.py` (`_render_param_widget`, `duration` branch)

**Implementation:** Replace the generic `duration` slider with constraint-aware logic:

```python
if param_name == "duration":
    enum_opts = get_options_for_param(model, param_name)
    min_val, max_val = get_range_for_param(model, param_name)

    if enum_opts:
        # Wan 2.5 I2V: only 5s or 10s
        int_opts = [int(x) if not isinstance(x, str) else int(x) for x in enum_opts]
        idx = int_opts.index(default) if default in int_opts else 0
        return st.selectbox(
            "Duration (s)", options=int_opts, index=idx, key=key_prefix,
        )

    # Slider with model-specific range
    dur_min = int(min_val) if min_val is not None else 1
    dur_max = int(max_val) if max_val is not None else 15
    dur_default = default if isinstance(default, int) else 5
    # Clamp default to range
    dur_default = max(dur_min, min(dur_max, dur_default))
    return st.slider(
        "Duration (s)", dur_min, dur_max, value=dur_default, step=1, key=key_prefix,
    )
```

**Verification:** Wan 2.7 T2V slider starts at 2. Wan 2.5 I2V shows dropdown [5, 10].
Seedance slider goes from -1 to 15.

**Step 5:** Commit: `feat: schema-driven duration widget`

---

### Task 2.3: Update resolution and aspect_ratio widgets

**Objective:** Use model-specific enum options.

**Files:**
- Modify: `app.py` (`_render_param_widget`, `resolution` and `aspect_ratio` branches)

**Implementation:**

```python
if param_name == "resolution":
    options = get_options_for_param(model, param_name) or ["480p", "720p", "1080p"]
    idx = options.index(default) if default in options else 1
    return st.selectbox("Resolution", options=options, index=idx, key=key_prefix)

if param_name == "aspect_ratio":
    options = get_options_for_param(model, param_name) or ["16:9", "9:16", "1:1", "4:3", "adaptive"]
    idx = options.index(default) if default in options else 0
    return st.selectbox("Aspect Ratio", options=options, index=idx, key=key_prefix)
```

**Verification:**
- Wan 2.7 T2V: resolution → [720p, 1080p]; aspect_ratio → [16:9, 9:16, 1:1, 4:3, 3:4]
- Seedance: resolution → [480p, 720p, 1080p]; aspect_ratio → [16:9, 4:3, 1:1, 3:4, 9:16, 21:9, 9:21, adaptive]

**Step 5:** Commit: `feat: schema-driven resolution and aspect_ratio widgets`

---

### Task 2.4: Update pipeline_type widget for TRELLIS 2

**Objective:** Use the corrected enum from the live schema.

**Files:**
- Modify: `app.py` (`_render_param_widget`, `pipeline_type` branch)

**Implementation:**

```python
if param_name == "pipeline_type":
    options = get_options_for_param(model, param_name) or ["512_fast", "1024_cascade", "2048_quality"]
    idx = options.index(default) if default in options else 1
    return st.selectbox(
        "Quality pipeline",
        options=options,
        index=idx,
        key=key_prefix,
        help=(
            "Fast is cheaper; cascade is balanced; "
            "quality is slowest/highest detail."
        ),
    )
```

**Verification:** TRELLIS 2 shows ['512', '1024', '1024_cascade', '1536_cascade'].

**Step 5:** Commit: `feat: schema-driven pipeline_type widget`

---

## Phase 3: Validation Layer — Pre-Submit Checks

### Task 3.1: Add `validate_params()` function

**Objective:** Validate all form kwargs against model constraints before API call.

**Files:**
- Create: `src/validation.py`

**Implementation:**

```python
"""Pre-submit validation against live Replicate model schemas."""

from __future__ import annotations

from .models_config import ModelConfig, get_options_for_param, get_range_for_param


class ValidationError(Exception):
    """User-friendly validation error."""
    pass


def validate_params(model: ModelConfig, kwargs: dict) -> None:
    """Raise ValidationError if any parameter is invalid for this model.

    Checks:
    - Enum parameters: value must be in allowed set
    - Range parameters: value must be within min/max
    - Nullable parameters: None is allowed (skip check)
    """
    errors: list[str] = []

    for pname, value in kwargs.items():
        if pname in ("_uploaded_image", "image", "prompt", "progress_callback"):
            continue

        nullable = model.param_constraints.get(pname, {}).get("nullable", False)
        if value is None:
            if nullable:
                continue
            errors.append(f"{pname}: cannot be None")
            continue

        # Enum check
        enum_vals = get_options_for_param(model, pname)
        if enum_vals is not None:
            # For numeric enums (like duration for Wan 2.5), compare as int
            try:
                str_vals = [str(v) for v in enum_vals]
                if isinstance(value, bool):
                    pass  # booleans can't match string enums
                elif str(value) not in str_vals:
                    errors.append(
                        f"{pname}: {value!r} not in allowed values {enum_vals}"
                    )
                    continue
            except Exception:
                errors.append(f"{pname}: invalid value {value!r}")
                continue

        # Range check
        min_val, max_val = get_range_for_param(model, pname)
        if isinstance(value, (int, float)):
            if min_val is not None and value < min_val:
                errors.append(
                    f"{pname}: {value} is below minimum {min_val}"
                )
            if max_val is not None and value > max_val:
                errors.append(
                    f"{pname}: {value} is above maximum {max_val}"
                )

    if errors:
        raise ValidationError("\n".join(errors))
```

**Step 5:** Commit: `feat: add pre-submit parameter validation`

---

### Task 3.2: Wire validation into app.py generation flow

**Objective:** Call `validate_params()` before `replicate.predictions.create()`.

**Files:**
- Modify: `app.py` (generation flow, ~line 270-305)

**Implementation:** Add a validation block before the model dispatch:

```python
if kwargs is not None:
    # ── Validate before paid call ──
    try:
        from src.validation import validate_params
        validate_params(model, kwargs)
    except Exception as exc:
        st.error(f"Invalid parameters:\n\n{exc}")
        st.stop()

    with st.status(...):
        ...
```

**Step 5:** Commit: `feat: wire pre-submit validation into generation flow`

---

## Phase 4: Tests

### Task 4.1: Add model schema conformance tests

**Objective:** Ensure every model's param_constraints match the live schema defaults.

**Files:**
- Create: `tests/test_model_constraints.py`

**Implementation:** See test file for inline tests.

**Step 5:** Commit: `test: add model constraint conformance tests`

---

## Phase 5: Documentation

### Task 5.1: Update ROADMAP.md

**Objective:** Mark v0.2.1 and v0.3.0 as implemented.

**Files:**
- Modify: `ROADMAP.md`

**Step 5:** Commit: `docs: mark v0.2.1 and v0.3.0 as implemented in ROADMAP`

---

## Phase 6: Browser QA

### Task 6.1: Browser QA of all model controls

**Objective:** Open the running app and verify each model's controls match the schema.

**Files:** None (verification only)

**Checks:**
- [ ] Wan 2.7 T2V: duration slider 2–15, resolution [720p, 1080p], aspect_ratio [16:9, 9:16, 1:1, 4:3, 3:4]
- [ ] Wan 2.5 I2V: duration dropdown [5, 10], resolution [720p, 1080p]
- [ ] Seedance 2.0: duration slider -1–15, resolution [480p, 720p, 1080p], aspect_ratio includes 21:9, 9:21, adaptive
- [ ] Hunyuan3D-2: steps 20-50, octree_resolution dropdown [256, 384, 512]
- [ ] TRELLIS 2: pipeline_type [512, 1024, 1024_cascade, 1536_cascade]

---

## Summary

| Phase | Tasks | Status |
|-------|-------|--------|
| 1: Data Layer | 1.1–1.6 (ModelConfig + constraints for all 5 models) | Pending |
| 2: UI Layer | 2.1–2.4 (Schema-driven widgets) | Pending |
| 3: Validation | 3.1–3.2 (Pre-submit validation) | Pending |
| 4: Tests | 4.1 (Constraint conformance tests) | Pending |
| 5: Docs | 5.1 (ROADMAP update) | Pending |
| 6: QA | 6.1 (Browser verification) | Pending |
