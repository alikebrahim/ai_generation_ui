"""Workflow filter and archetype-specific media inputs for the Video tab."""

from __future__ import annotations

import streamlit as st

from src.models_config import VIDEO_MODELS, ModelConfig

VIDEO_WORKFLOW_FILTERS: list[tuple[str, str]] = [
    ("all", "All models"),
    ("text_to_video", "Make from text"),
    ("image_to_video", "Animate an image"),
    ("motion_transfer", "Motion from video"),
    ("edit_video", "Edit a video"),
    ("multimodal", "Multimodal / references"),
]


def filter_models_for_workflow(
    models: list[ModelConfig],
    workflow_key: str,
) -> list[ModelConfig]:
    """Return models matching the workflow filter."""
    if workflow_key == "all":
        return list(models)
    return [m for m in models if workflow_key in getattr(m, "workflow_tags", [])]


def render_workflow_filter() -> str:
    """Render workflow segmented control and return selected filter key."""
    labels = {key: label for key, label in VIDEO_WORKFLOW_FILTERS}
    options = [key for key, _ in VIDEO_WORKFLOW_FILTERS]
    default = st.session_state.get("video_workflow_filter", "all")
    if default not in options:
        default = "all"
    selected = st.segmented_control(
        "What do you want to do?",
        options=options,
        default=default,
        format_func=lambda key: labels[key],
        key="video_workflow_filter",
        help="Narrows the model list to ones that support this kind of task.",
    )
    return selected or default


def _file_uploader(
    model: ModelConfig,
    param_name: str,
    *,
    required: bool = False,
    key_suffix: str = "",
    multiple: bool = False,
) -> None:
    """Render one (or multi) file uploader into session kwargs via caller's dict."""
    extensions = model.file_input_params.get(param_name, ["png", "jpg", "jpeg"])
    label = model.media_roles.get(
        param_name, param_name.replace("_", " ").title()
    )
    is_ref_list = "reference" in param_name
    use_multi = multiple or is_ref_list
    uploaded = st.file_uploader(
        label + (" *" if required else " (optional)"),
        type=extensions,
        key=f"wf_{model.name}_{param_name}{key_suffix}",
        accept_multiple_files=use_multi,
    )
    return uploaded


def render_archetype_media_wide(
    model: ModelConfig,
    kwargs: dict,
) -> None:
    """Motion transfer and video edit: large media uploads in the preview column."""
    if model.workflow_archetype == "motion_transfer":
        st.markdown("#### Character and driving video")
        col_a, col_b = st.columns(2)
        with col_a:
            img = _file_uploader(model, "image", required=True)
            kwargs["_uploaded_image"] = img
            if img is not None:
                st.image(img, caption="Character preview", width="stretch")
        with col_b:
            vid = _file_uploader(model, "video", required=True)
            kwargs["_uploaded_video"] = vid
            if vid is not None:
                st.video(vid)
        if model.name == "kling-v3-motion":
            st.caption(
                "Optional: add a short prompt below (Advanced) to guide elements "
                "or background motion."
            )
        return

    if model.workflow_archetype == "video_edit":
        st.markdown("#### Source video and edit instructions")
        vid = _file_uploader(model, "video", required=True)
        kwargs["_uploaded_video"] = vid
        if vid is not None:
            st.video(vid)
        st.caption("Describe what to change — keep the rest of the clip as-is.")
        kwargs["prompt"] = st.text_area(
            model.media_roles.get("prompt", "Edit instructions"),
            placeholder="e.g. Change the jacket to red leather…",
            height=120,
            key=f"edit_prompt_{model.name}",
        )
        return


def _first_frame_param(model: ModelConfig) -> str | None:
    """Return the provider schema key used for a start/first-frame upload."""
    if "start_image" in model.file_input_params:
        return "start_image"
    if "image" in model.file_input_params:
        return "image"
    if model.supports_image:
        return "image"
    return None


def render_multimodal_media_sections(model: ModelConfig, kwargs: dict) -> None:
    """Start/end frame and optional single reference uploads."""
    with st.container(border=True):
        st.markdown("#### Frames and references")
        first_param = _first_frame_param(model)
        if first_param is not None:
            start = _file_uploader(model, first_param)
            if start is not None:
                kwargs[f"_uploaded_{first_param}"] = start
                st.image(start, caption="Start frame", width="stretch")

        if "end_image" in model.file_input_params or "last_frame_image" in (
            model.file_input_params
        ):
            add_end = st.checkbox(
                "Add an end frame (optional)",
                key=f"end_chk_{model.name}",
            )
            if add_end:
                end_param = (
                    "end_image"
                    if "end_image" in model.file_input_params
                    else "last_frame_image"
                )
                end = _file_uploader(model, end_param)
                if end is not None:
                    kwargs[f"_uploaded_{end_param}"] = end

        with st.expander("Reference image or video (optional)", expanded=False):
            st.caption(
                "You can select multiple references. Mention them in your prompt "
                "(e.g. <<<image_1>>> or [Image1] depending on the model docs)."
            )
            if "reference_images" in model.file_input_params:
                ref_img = _file_uploader(model, "reference_images")
                if ref_img is not None:
                    kwargs["_uploaded_reference_images"] = ref_img
            if "reference_video" in model.file_input_params:
                ref_vid = _file_uploader(model, "reference_video")
                if ref_vid is not None:
                    kwargs["_uploaded_reference_video"] = ref_vid
            if "reference_videos" in model.file_input_params:
                ref_vid = _file_uploader(
                    model, "reference_videos", key_suffix="_rv"
                )
                if ref_vid is not None:
                    kwargs["_uploaded_reference_videos"] = ref_vid
            if "reference_audios" in model.file_input_params:
                ref_audio = _file_uploader(
                    model, "reference_audios", key_suffix="_ra"
                )
                if ref_audio is not None:
                    kwargs["_uploaded_reference_audios"] = ref_audio


def model_caption(model: ModelConfig) -> str:
    """One-line helper under the model selector."""
    if model.output_notes:
        return model.output_notes
    if model.pricing_notes:
        return model.pricing_notes
    return ""


def resolve_video_model_selection(
    filtered_models: list[ModelConfig],
) -> ModelConfig:
    """Keep a stable model selection across workflow filter changes."""
    if not filtered_models:
        return VIDEO_MODELS[0]
    names = [m.name for m in filtered_models]
    current = st.session_state.get("video_model_name")
    if current not in names:
        current = names[0]
        st.session_state["video_model_name"] = current
    idx = names.index(current)
    chosen = st.selectbox(
        "Choose a model",
        options=names,
        index=idx,
        format_func=lambda n: next(
            m.display_name for m in filtered_models if m.name == n
        ),
        key="video_model_name",
    )
    return next(m for m in filtered_models if m.name == chosen)
