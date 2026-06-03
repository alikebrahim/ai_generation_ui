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


_VALIDATION_SKIP = frozenset({
    "_uploaded_image",
    "image",
    "prompt",
    "progress_callback",
    "reference_images",
    "reference_videos",
    "reference_audios",
})


def validate_params(model: ModelConfig, kwargs: dict) -> None:
    """Raise ValidationError if any parameter is invalid for this model.

    Checks performed (driven by model.param_constraints):

    - **Enum params**: value must be in the allowed set.
    - **Range params**: numeric value must be within min/max.
    - **Nullable params**: None is allowed; other params skip null check.
    """
    errors: list[str] = []

    for pname, value in kwargs.items():
        if pname in _VALIDATION_SKIP:
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

    if errors:
        raise ValidationError("\n".join(errors))
