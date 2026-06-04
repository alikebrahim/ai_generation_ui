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
from src.ui.request_preview import render_request_preview
from src.ui.video_workflow import (
    render_archetype_media_wide,
    render_multimodal_media_sections,
)


def _threed_model_caption(model: ModelConfig) -> str:
    """Short plain-English description for the selected 3D model."""
    captions = {
        "hunyuan-3d-3.1": (
            "Create a 3D model from a text description or one subject image."
        ),
        "hunyuan3d-2mv": (
            "Upload a front view (required). Side/back views can improve consistency."
        ),
        "text2tex": (
            "Upload an .obj mesh, then describe the texture you want applied."
        ),
        "adirik-texture": (
            "Upload an untextured mesh, then describe how the surface should look."
        ),
        "rodin": (
            "Describe the 3D model. Optionally add a reference image for likeness."
        ),
    }
    if model.name in captions:
        return captions[model.name]
    return "Upload one clear subject image for image-to-3D generation."


def normalize_file_kwargs(model: ModelConfig, kwargs: dict) -> dict:
    """Map ``_uploaded_*`` form keys to Replicate payload parameter names."""
    out = dict(kwargs)
    uploaded = out.pop("_uploaded_image", None)
    if uploaded is not None and model.supports_image and "image" not in out:
        out["image"] = uploaded
    for key in list(out.keys()):
        if not key.startswith("_uploaded_"):
            continue
        param = key.removeprefix("_uploaded_")
        value = out.pop(key)
        if param == "images":
            out["_uploaded_images"] = value
        else:
            out[param] = value
    return out


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
        "mode": "Quality tier",
        "character_orientation": "Character facing",
        "video_reference_type": "Reference video mode",
        "cut_first_second": "Trim first second of output",
        "keep_original_sound": "Keep original sound",
        "multi_prompt": "Multi-shot JSON",
    }
    if model and param_name in getattr(model, "media_roles", {}):
        return model.media_roles[param_name]
    return labels.get(param_name, param_name.replace("_", " ").title())


def render_param_widget(model: ModelConfig, param_name: str, advanced: bool = False):
    """Render one parameter widget with model-aware defaults."""
    default = model.defaults.get(param_name)
    key_prefix = f"{model.name}_{'adv_' if advanced else ''}{param_name}"

    if model and param_name in model.file_input_params:
        return None
    if param_name in {"image", "prompt", "images"}:
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
        st.caption(_threed_model_caption(model))
    elif model.supports_image and not model.requires_image:
        st.caption("Use text only, or optionally add an image to guide the result.")

    kwargs: dict = {}
    archetype = model.workflow_archetype
    media_in_preview = archetype in ("motion_transfer", "video_edit")
    selected_mode = _render_input_mode_selector(model)
    if selected_mode is not None:
        kwargs["_generation_mode"] = selected_mode
    prompt_visible = model.supports_text and selected_mode != "image"
    image_visible = (
        model.supports_image
        and selected_mode != "text"
        and not model.file_input_params
    )
    if archetype == "video_edit":
        prompt_visible = False
        image_visible = False
    elif archetype == "motion_transfer":
        prompt_visible = False
        image_visible = False
    elif archetype == "multimodal_video":
        image_visible = False
    rodin_reference_visible = model.name == "rodin" and selected_mode == "reference"
    preview_col, controls_col = st.columns([3, 1.05], vertical_alignment="top")

    with preview_col:
        with st.container(border=True):
            st.markdown(
                "<span class='ai-prediction-preview-anchor'></span>",
                unsafe_allow_html=True,
            )
            if media_in_preview:
                render_archetype_media_wide(model, kwargs)
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
            elif model.name in ("seedance-2.0", "seedance-2.0-fast", "gen-4.5"):
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
    if archetype == "multimodal_video":
        render_multimodal_media_sections(model, kwargs)
    elif rodin_reference_visible:
        with st.container(border=True):
            st.markdown("#### Reference image")
            uploaded = st.file_uploader(
                friendly_label("images", model),
                type=model.file_input_params.get(
                    "images", ["png", "jpg", "jpeg", "webp"]
                ),
                key=f"img_{model.name}_reference",
                help="Optional likeness guide — text prompt is still required.",
            )
            kwargs["_uploaded_images"] = uploaded
            if uploaded is not None:
                st.image(uploaded, caption="Reference preview", width="stretch")
    elif not model.supports_text and not model.file_input_params:
        st.info("This model uses image input only (no text prompt).")
    else:
        st.caption("No prompt inputs are needed for the selected mode.")

    with controls_box:
        st.markdown("#### Balanced controls")
        skip_balanced = {"prompt", "image", "images", "video"}
        if archetype == "multimodal_video":
            skip_balanced |= {
                "start_image",
                "end_image",
                "last_frame_image",
                "reference_images",
                "reference_video",
                "reference_videos",
                "reference_audios",
            }
        visible_params = [
            p
            for p in model.balanced_params
            if p not in skip_balanced and p not in model.file_input_params
        ]
        for param_name in visible_params:
            if param_name in model.file_input_params:
                extensions = model.file_input_params[param_name]
                required = param_name in model.required_file_params
                uploaded = st.file_uploader(
                    friendly_label(param_name, model)
                    + ("" if required else " (optional)"),
                    type=extensions,
                    key=f"file_bal_{model.name}_{param_name}",
                )
                kwargs[f"_uploaded_{param_name}"] = uploaded
                if uploaded is not None and param_name.endswith("_image"):
                    st.image(uploaded, caption="Preview", width="stretch")
                continue
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
            and p not in model.file_input_params
        ]
        if model.name == "rodin" and selected_mode == "reference":
            advanced_params = [p for p in advanced_params if p != "images"]
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
                    if param_name in model.file_input_params:
                        extensions = model.file_input_params[param_name]
                        uploaded = st.file_uploader(
                            friendly_label(param_name, model) + " (optional)",
                            type=extensions,
                            key=f"file_adv_{model.name}_{param_name}",
                        )
                        kwargs[f"_uploaded_{param_name}"] = uploaded
                        if uploaded is not None and param_name.endswith("_image"):
                            st.image(uploaded, caption="Preview", width="stretch")
                        continue
                    value = render_param_widget(model, param_name, advanced=True)
                    if value is not None:
                        kwargs[param_name] = value

        render_request_preview(model, kwargs)

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

    if model.requires_text and not str(kwargs.get("prompt", "")).strip():
        if archetype != "video_edit":
            st.error("Please enter a prompt.")
            return None
    if model.required_one_of:
        for group in model.required_one_of:
            satisfied = False
            for param in group:
                if kwargs.get(f"_uploaded_{param}") is not None:
                    satisfied = True
                    break
                val = kwargs.get(param)
                if val is not None and (
                    not isinstance(val, str) or bool(str(val).strip())
                ):
                    satisfied = True
                    break
            if not satisfied:
                labels = " or ".join(
                    model.media_roles.get(p, p) for p in group
                )
                st.error(f"Please provide {labels}.")
                return None
    if model.requires_image and kwargs.get("_uploaded_image") is None:
        if not model.file_input_params:
            st.error("Please upload an image.")
            return None
    for param_name in model.required_file_params:
        upload_key = f"_uploaded_{param_name}"
        if param_name == "images":
            upload_key = "_uploaded_images"
        if kwargs.get(upload_key) is None:
            st.error(f"Please upload: {friendly_label(param_name, model)}.")
            return None

    return normalize_file_kwargs(model, kwargs)
