"""Pre-submit parameter validation against live Replicate model schemas.

Called by app.py before creating a Replicate prediction. Validates all
user-supplied parameters against the model's param_constraints so the
user gets a friendly st.error() instead of a Replicate 422 error and
no money is spent on invalid generation requests.
"""

from __future__ import annotations

from .models_config import ModelConfig, get_options_for_param, get_range_for_param


class ValidationError(Exception):
    """Aggregates one or more user-friendly validation messages."""


_VALIDATION_SKIP = frozenset(
    {
        "_uploaded_image",
        "_uploaded_images",
        "image",
        "progress_callback",
        "reference_images",
        "reference_videos",
        "reference_audios",
        "obj_file",
        "shape_path",
        "front_image",
        "back_image",
        "left_image",
        "right_image",
        "images",
        "video",
        "start_image",
        "end_image",
        "last_frame_image",
        "reference_video",
        "keyframe_images",
        "image_input",
        "input_images",
        "mask",
        "style_reference_images",
    }
)


def _is_provided(value: object) -> bool:
    """Return True when a parameter carries a meaningful user value."""
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    return True


def validate_params(model: ModelConfig, kwargs: dict) -> None:
    """Raise ValidationError if any parameter is invalid for this model.

    Checks performed:

    - **Enum params**: value must be in the allowed set.
    - **Range params**: numeric value must be within min/max.
    - **Nullable params**: None is allowed; other params skip null check.
    - **Mutual exclusion**: if model declares mutual_exclusion groups, only
      one parameter in each group may have a non-empty / non-None value.
    """
    errors: list[str] = []

    # ── Required-one-of checks ─────────────────────────────────────────
    for group in getattr(model, "required_one_of", []):
        if not any(_is_provided(kwargs.get(p)) for p in group):
            group_label = " or ".join(repr(p) for p in group)
            errors.append(f"One of {group_label} is required.")

    # ── Mutual-exclusion checks ────────────────────────────────────────
    for group in getattr(model, "mutual_exclusion", []):
        provided = [p for p in group if _is_provided(kwargs.get(p))]
        if len(provided) > 1:
            labels = ", ".join(repr(p) for p in provided)
            group_label = " or ".join(repr(p) for p in group)
            errors.append(f"Only one of {group_label} can be provided; got {labels}.")

    file_params = frozenset(getattr(model, "file_input_params", {}).keys())

    for pname, value in kwargs.items():
        if pname in _VALIDATION_SKIP or pname in file_params:
            continue

        constraints = model.param_constraints.get(pname, {})
        nullable = constraints.get("nullable", False)

        # ── Null handling ──
        if value is None:
            if nullable:
                continue
            errors.append(f"{pname}: cannot be None")
            continue

        # ── Enum check ──
        enum_vals = get_options_for_param(model, pname)
        if enum_vals is not None:
            # Compare as strings (handles mixed str/int enums like [5, 10])
            str_vals = {str(v) for v in enum_vals}
            if isinstance(value, bool):
                # booleans are a subtype of int; skip enum matching
                pass
            elif str(value) not in str_vals:
                errors.append(
                    f"{pname}: {value!r} is not allowed. "
                    f"Supported values: {sorted(enum_vals)}"
                )
                continue

        # ── Range check ──
        min_val, max_val = get_range_for_param(model, pname)
        if isinstance(value, (int, float)) and not isinstance(value, bool):
            if min_val is not None and value < min_val:
                errors.append(
                    f"{pname}: {value} is below the minimum value of {min_val}"
                )
            if max_val is not None and value > max_val:
                errors.append(
                    f"{pname}: {value} is above the maximum value of {max_val}"
                )
        elif isinstance(value, str) and value:
            constraints = model.param_constraints.get(pname, {})
            str_max = constraints.get("max")
            if (
                str_max is not None
                and isinstance(str_max, int)
                and len(value) > str_max
            ):
                errors.append(
                    f"{pname}: text is {len(value)} characters; "
                    f"maximum is {str_max} characters."
                )

    if errors:
        raise ValidationError("\n".join(errors))
