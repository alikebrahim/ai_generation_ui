"""Generic parameter form rendering."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from src import utils as app_utils
from src.models_config import (
    ModelConfig,
    get_options_for_param,
    get_range_for_param,
)
from src.pricing import calculate_cost


def friendly_label(param_name: str, model: ModelConfig | None = None) -> str:
    """Convert API-ish parameter names into readable labels."""
    labels = {
        "enable_prompt_expansion": "Improve prompt automatically",
        "octree_resolution": "Mesh resolution",
        "decimation_target": "Mesh polygon budget",
        "generate_audio": "Generate audio",
        "generate_model": "Generate 3D model",
        "generate_video": "Generate preview video",
        "preprocess_image": "Clean up image first",
    }
    if model and param_name in getattr(model, "media_roles", {}):
        return model.media_roles[param_name]
    return labels.get(param_name, param_name.replace("_", " ").title())


def render_param_widget(model: ModelConfig, param_name: str, advanced: bool = False):
    """Render one parameter widget with model-aware defaults."""
    default = model.defaults.get(param_name)
    key_prefix = f"{model.name}_{'adv_' if advanced else ''}{param_name}"

    if param_name in {"image", "prompt"}:
        return None
    if param_name == "duration":
        enum_opts = get_options_for_param(model, param_name)
        min_val, max_val = get_range_for_param(model, param_name)

        if enum_opts:
            int_opts = sorted(enum_opts)
            dur_default = default if isinstance(default, int) else int_opts[0]
            idx = int_opts.index(dur_default) if dur_default in int_opts else 0
            return st.selectbox(
                "Duration (s)",
                options=int_opts,
                index=idx,
                key=key_prefix,
                help="Shorter is faster; longer clips may cost more.",
            )

        dur_min = int(min_val) if min_val is not None else 1
        dur_max = int(max_val) if max_val is not None else 15
        dur_default = default if isinstance(default, int) else 5
        dur_default = max(dur_min, min(dur_max, dur_default))
        return st.slider(
            "Duration (s)",
            dur_min,
            dur_max,
            value=dur_default,
            step=1,
            key=key_prefix,
            help="Shorter is faster; longer clips may cost more.",
        )
    if param_name == "seed":
        seed_default = default if isinstance(default, int) else -1
        if model.model_type == "video":
            val = st.number_input(
                "Seed (-1 = random)",
                value=seed_default,
                step=1,
                key=key_prefix,
                help="Leave at -1 to let the model pick a fresh random seed.",
            )
            return None if val < 0 else val
        return st.number_input(
            "Seed",
            value=seed_default,
            step=1,
            key=key_prefix,
        )
    if param_name == "aspect_ratio":
        options = get_options_for_param(model, param_name) or [
            "16:9",
            "9:16",
            "1:1",
            "4:3",
            "adaptive",
        ]
        idx = options.index(default) if default in options else 0
        return st.selectbox(
            "Aspect ratio",
            options=options,
            index=idx,
            key=key_prefix,
            help="Pick the shape that matches where you plan to watch it.",
        )
    if param_name == "resolution":
        options = get_options_for_param(model, param_name) or [
            "480p",
            "720p",
            "1080p",
        ]
        idx = options.index(default) if default in options else 1
        return st.selectbox(
            "Resolution",
            options=options,
            index=idx,
            key=key_prefix,
            help="Higher resolution can look better but may take longer.",
        )
    if param_name == "pipeline_type":
        options = get_options_for_param(model, param_name) or [
            "512",
            "1024",
            "1024_cascade",
            "1536_cascade",
        ]
        idx = options.index(default) if default in options else 1
        return st.selectbox(
            "Quality pipeline",
            options=options,
            index=idx,
            key=key_prefix,
            help=(
                "512 is fastest/cheapest; 1024_cascade is balanced; "
                "1536_cascade is highest quality."
            ),
        )
    if isinstance(default, list):
        st.caption(
            f"{friendly_label(param_name, model)} is available later once list inputs "
            "are exposed safely in the UI."
        )
        return None
    enum_opts = get_options_for_param(model, param_name)
    if enum_opts:
        idx = enum_opts.index(default) if default in enum_opts else 0
        return st.selectbox(
            friendly_label(param_name, model),
            options=enum_opts,
            index=idx,
            key=key_prefix,
        )
    if isinstance(default, bool):
        return st.checkbox(
            friendly_label(param_name, model), value=default, key=key_prefix
        )
    if isinstance(default, float):
        min_val, max_val = get_range_for_param(model, param_name)
        return st.number_input(
            friendly_label(param_name, model),
            value=default,
            min_value=float(min_val) if min_val is not None else None,
            max_value=float(max_val) if max_val is not None else None,
            key=key_prefix,
        )
    if isinstance(default, int):
        min_val, max_val = get_range_for_param(model, param_name)
        return st.number_input(
            friendly_label(param_name, model),
            value=default,
            step=1,
            min_value=int(min_val) if min_val is not None else None,
            max_value=int(max_val) if max_val is not None else None,
            key=key_prefix,
        )
    return st.text_input(
        friendly_label(param_name, model),
        value=str(default) if default else "",
        key=key_prefix,
    )


def _render_input_mode_selector(model: ModelConfig) -> str | None:
    """Render a compact mode selector when the model exposes multiple modes."""
    if not model.generation_modes:
        return None

    options = [mode for mode, _ in model.generation_modes]
    labels = {mode: label for mode, label in model.generation_modes}
    default_mode = model.default_generation_mode or options[0]
    index = options.index(default_mode) if default_mode in options else 0
    selected_mode = st.radio(
        "Create from",
        options=options,
        index=index,
        format_func=lambda mode: labels.get(mode, mode),
        horizontal=True,
        key=f"mode_{model.name}",
        help="Choose one input style. Only the relevant input will be shown.",
    )
    return selected_mode


def render_generation_form(
    model: ModelConfig,
    preview_renderer: Callable[[], None] | None = None,
    model_selector_renderer: Callable[[], None] | None = None,
) -> dict | None:
    """Render the generation workspace for a model."""
    st.subheader(f"Generate with {model.display_name}")

    if model.model_type == "3d":
        if model.name == "hunyuan-3d-3.1":
            st.caption(
                "This model can create a 3D model from text or from one subject image."
            )
        else:
            st.caption(
                "Current 3D models are image-to-3D. Upload one clear subject image."
            )
    elif model.supports_image and not model.requires_image:
        st.caption("Use text only, or optionally add an image to guide the result.")

    selected_mode = _render_input_mode_selector(model)
    prompt_visible = model.supports_text and selected_mode != "image"
    image_visible = model.supports_image and selected_mode != "text"

    kwargs: dict = {}
    preview_col, controls_col = st.columns([3, 1.05], vertical_alignment="top")

    with preview_col:
        with st.container(border=True):
            st.markdown(
                "<span class='ai-prediction-preview-anchor'></span>",
                unsafe_allow_html=True,
            )
            if preview_renderer is not None:
                preview_renderer()
            else:
                st.markdown("#### Prediction status / preview")
                st.info("Run a generation and the preview will stay open here.")

    controls_box = controls_col.container(border=True)

    st.markdown("<div style='height: 0.7rem'></div>", unsafe_allow_html=True)
    if model_selector_renderer is not None:
        with st.container(border=True):
            model_selector_renderer()
        st.markdown("<div style='height: 0.7rem'></div>", unsafe_allow_html=True)

    def render_text_prompt() -> None:
        with st.container(border=True):
            st.markdown("#### Text prompt")
            prompt_label = friendly_label("prompt", model)
            prompt_help = (
                "Be concrete: subject, motion, camera, style, lighting, mood."
            )
            kwargs["prompt"] = st.text_area(
                prompt_label,
                placeholder=(
                    f"Describe what you want {model.display_name} to generate…"
                ),
                height=140,
                help=prompt_help,
                label_visibility="collapsed",
            )

    def render_image_prompts() -> None:
        with st.container(border=True):
            st.markdown("#### Image prompts")
            upload_label = friendly_label("image", model)
            upload_help = (
                "Replicate accepts local file uploads. Keep files under 100 MB."
            )
            if model.model_type == "3d" and model.name == "hunyuan-3d-3.1":
                upload_help = (
                    "Optional — use a subject image OR the text prompt, not both. "
                    "Upload a clear subject image for best image-to-3D results."
                )
            elif model.name == "seedance-2.0":
                upload_help = (
                    "Optional first frame for image-to-video; leave empty for "
                    "text-to-video."
                )
            uploaded = st.file_uploader(
                upload_label + ("" if model.requires_image else " (optional)"),
                type=["png", "jpg", "jpeg", "webp"],
                key=f"img_{model.name}",
                help=upload_help,
            )
            kwargs["_uploaded_image"] = uploaded
            if uploaded is not None:
                st.image(uploaded, caption="Input preview", width="stretch")
                meta = app_utils.uploaded_file_metadata(uploaded)
                size_mb = (meta.get("size_bytes") or 0) / 1_000_000
                st.caption(f"{meta.get('filename')} · {size_mb:.2f} MB")

    if prompt_visible and image_visible:
        col_left, col_right = st.columns([1.1, 1.9], vertical_alignment="top")
        with col_left:
            render_text_prompt()
        with col_right:
            render_image_prompts()
    elif prompt_visible:
        render_text_prompt()
    elif image_visible:
        render_image_prompts()
    elif not model.supports_text:
        st.info("This model uses image input only (no text prompt).")
    else:
        st.caption("No prompt inputs are needed for the selected mode.")

    with controls_box:
        st.markdown("#### Balanced controls")
        visible_params = [
            p for p in model.balanced_params if p not in ("prompt", "image")
        ]
        for param_name in visible_params:
            value = render_param_widget(model, param_name)
            if value is not None or param_name == "seed":
                kwargs[param_name] = value

        duration = kwargs.get("duration")
        st.caption(
            "Estimated cost: "
            + app_utils.estimate_cost_label(
                model.replicate_id, duration, calculate_cost
            )
        )

        st.divider()
        advanced_params = [
            p
            for p in model.advanced_params
            if not isinstance(model.defaults.get(p), list)
        ]
        skipped_params = [p for p in model.advanced_params if p not in advanced_params]
        if advanced_params or skipped_params:
            with st.expander("Advanced controls", expanded=False):
                if skipped_params:
                    st.caption(
                        "Multi-reference inputs are intentionally hidden until the UI "
                        "can validate lists and files correctly: "
                        + ", ".join(skipped_params)
                    )
                for param_name in advanced_params:
                    value = render_param_widget(model, param_name, advanced=True)
                    if value is not None:
                        kwargs[param_name] = value

        st.markdown("<div style='height: 0.35rem'></div>", unsafe_allow_html=True)
        generate_label = (
            "Generate Video" if model.model_type == "video" else "Generate 3D Model"
        )
        generate_clicked = st.button(
            generate_label,
            type="primary",
            key=f"btn_{model.name}",
            use_container_width=True,
        )

    if not generate_clicked:
        return None

    if model.requires_text and not kwargs.get("prompt", "").strip():
        st.error("Please enter a prompt.")
        return None
    if model.requires_image and kwargs.get("_uploaded_image") is None:
        st.error("Please upload an image.")
        return None

    return kwargs
