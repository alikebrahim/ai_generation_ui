"""AI Generation Studio — Streamlit app for Replicate-powered video & 3D generation.

Usage:
    cd /home/tima/ai_generation_ui
    uv run streamlit run app.py
"""

from __future__ import annotations

import sys
from pathlib import Path
from time import monotonic

# Allow imports from src/ without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from src.config import check_token
from src.cost_tracker import (
    get_all_generations,
    get_stats_by_model,
    get_total_stats,
    init_db,
)
from src.models_config import THREED_MODELS, VIDEO_MODELS, ModelConfig
from src.models_config import get_options_for_param, get_range_for_param, is_param_nullable
from src.pricing import calculate_cost
from src.utils import (
    estimate_cost_label,
    format_cost,
    format_duration,
    format_timestamp,
    uploaded_file_metadata,
)

# ── Page config (must be first st call) ────────────────────────────

st.set_page_config(
    page_title="AI Generation Studio",
    page_icon="🎬",
    layout="wide",
)

# ── Check for API token before anything else ───────────────────────

try:
    check_token()
except RuntimeError as err:
    st.error(str(err))
    st.stop()

# ── Init DB on first load ──────────────────────────────────────────

init_db()

# ── Title ──────────────────────────────────────────────────────────

st.title("🎬 AI Generation Studio")
st.caption("Generate videos and 3D models with Replicate API")


# ═══════════════════════════════════════════════════════════════════
#  Helper: render generation form for any model
# ═══════════════════════════════════════════════════════════════════


def _friendly_label(param_name: str) -> str:
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
    return labels.get(param_name, param_name.replace("_", " ").title())


def _render_param_widget(model: ModelConfig, param_name: str, advanced: bool = False):
    """Render one parameter widget with model-aware defaults."""
    default = model.defaults.get(param_name)
    key_prefix = f"{model.name}_{'adv_' if advanced else ''}{param_name}"

    if param_name == "image" or param_name == "prompt":
        return None
    if param_name == "duration":
        enum_opts = get_options_for_param(model, param_name)
        min_val, max_val = get_range_for_param(model, param_name)

        if enum_opts:
            # Model with fixed duration options (e.g. Wan 2.5 I2V: only 5s or 10s)
            int_opts = sorted(enum_opts)
            dur_default = default if isinstance(default, int) else int_opts[0]
            idx = int_opts.index(dur_default) if dur_default in int_opts else 0
            return st.selectbox(
                "Duration (s)", options=int_opts, index=idx, key=key_prefix,
            )

        # Slider with model-specific range
        dur_min = int(min_val) if min_val is not None else 1
        dur_max = int(max_val) if max_val is not None else 15
        dur_default = default if isinstance(default, int) else 5
        dur_default = max(dur_min, min(dur_max, dur_default))
        return st.slider(
            "Duration (s)", dur_min, dur_max,
            value=dur_default, step=1, key=key_prefix,
        )
    if param_name == "seed":
        seed_default = default if isinstance(default, int) else -1
        if model.model_type == "video":
            val = st.number_input(
                "Seed (-1 = random)",
                value=seed_default,
                step=1,
                key=key_prefix,
            )
            return None if val < 0 else val
        return st.number_input("Seed", value=seed_default, step=1, key=key_prefix)
    if param_name == "aspect_ratio":
        options = get_options_for_param(model, param_name) or [
            "16:9", "9:16", "1:1", "4:3", "adaptive",
        ]
        idx = options.index(default) if default in options else 0
        return st.selectbox("Aspect Ratio", options=options, index=idx, key=key_prefix)
    if param_name == "resolution":
        options = get_options_for_param(model, param_name) or [
            "480p", "720p", "1080p",
        ]
        idx = options.index(default) if default in options else 1
        return st.selectbox("Resolution", options=options, index=idx, key=key_prefix)
    if param_name == "pipeline_type":
        options = get_options_for_param(model, param_name) or [
            "512", "1024", "1024_cascade", "1536_cascade",
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
        st.caption(f"{_friendly_label(param_name)}: coming in a future UI pass")
        return None
    if isinstance(default, bool):
        return st.checkbox(_friendly_label(param_name), value=default, key=key_prefix)
    if isinstance(default, float):
        min_val, max_val = get_range_for_param(model, param_name)
        return st.number_input(
            _friendly_label(param_name),
            value=default,
            min_value=float(min_val) if min_val is not None else None,
            max_value=float(max_val) if max_val is not None else None,
            key=key_prefix,
        )
    if isinstance(default, int):
        min_val, max_val = get_range_for_param(model, param_name)
        return st.number_input(
            _friendly_label(param_name),
            value=default,
            step=1,
            min_value=int(min_val) if min_val is not None else None,
            max_value=int(max_val) if max_val is not None else None,
            key=key_prefix,
        )
    return st.text_input(
        _friendly_label(param_name),
        value=str(default) if default else "",
        key=key_prefix,
    )


def _render_generation_form(model: ModelConfig) -> dict | None:
    """Render Balanced + Advanced param form for a model."""
    st.subheader(f"Generate with {model.display_name}")

    if model.model_type == "3d":
        st.caption("Current 3D models are Image-to-3D. Upload a clear subject image.")
    elif model.supports_image and not model.requires_image:
        st.caption("Use text only, or optionally add an image to guide the result.")

    kwargs: dict = {}
    col_left, col_right = st.columns([2, 1])

    with col_left:
        if model.supports_text:
            kwargs["prompt"] = st.text_area(
                "Prompt",
                placeholder=f"Describe what you want {model.display_name} to generate…",
                height=100,
                help="Be concrete: subject, motion, camera, style, lighting, mood.",
            )
        else:
            st.info("This model uses image input only (no text prompt).")

    with col_right:
        if model.supports_image:
            uploaded = st.file_uploader(
                "Upload Image" + ("" if model.requires_image else " (optional)"),
                type=["png", "jpg", "jpeg", "webp"],
                key=f"img_{model.name}",
                help="Replicate accepts local file uploads. Keep files under 100 MB.",
            )
            kwargs["_uploaded_image"] = uploaded
            if uploaded is not None:
                st.image(uploaded, caption="Input preview", use_container_width=True)
                meta = uploaded_file_metadata(uploaded)
                size_mb = (meta.get("size_bytes") or 0) / 1_000_000
                st.caption(f"{meta.get('filename')} · {size_mb:.2f} MB")
        else:
            st.caption("Text-only model")

    st.markdown("**Balanced controls**")
    cols = st.columns(3)
    visible_params = [p for p in model.balanced_params if p not in ("prompt", "image")]
    for i, param_name in enumerate(visible_params):
        with cols[i % 3]:
            value = _render_param_widget(model, param_name)
            if value is not None or param_name == "seed":
                kwargs[param_name] = value

    duration = kwargs.get("duration")
    st.info(
        "Estimated generation cost: "
        + estimate_cost_label(model.replicate_id, duration, calculate_cost)
        + " · Final cost is recorded after Replicate returns metrics."
    )

    advanced_params = [
        p for p in model.advanced_params if not isinstance(model.defaults.get(p), list)
    ]
    skipped_params = [p for p in model.advanced_params if p not in advanced_params]
    if advanced_params or skipped_params:
        with st.expander("⚙️ Advanced controls"):
            if skipped_params:
                st.caption(
                    "Multi-reference inputs are intentionally hidden until the UI can "
                    "validate lists/files correctly: " + ", ".join(skipped_params)
                )
            adv_cols = st.columns(3)
            for i, param_name in enumerate(advanced_params):
                with adv_cols[i % 3]:
                    value = _render_param_widget(model, param_name, advanced=True)
                    if value is not None:
                        kwargs[param_name] = value

    generate_label = (
        "Generate Video" if model.model_type == "video" else "Generate 3D Model"
    )
    if not st.button(generate_label, type="primary", key=f"btn_{model.name}"):
        return None

    if model.requires_text and not kwargs.get("prompt", "").strip():
        st.error("Please enter a prompt.")
        return None
    if model.requires_image and kwargs.get("_uploaded_image") is None:
        st.error("Please upload an image.")
        return None

    return kwargs


# ═══════════════════════════════════════════════════════════════════
#  TABS
# ═══════════════════════════════════════════════════════════════════

tab_video, tab_3d, tab_history = st.tabs(["🎥 Video", "🧊 3D", "📊 History"])


# ──────────────────────────────────────────────────────────────────
#  TAB: Video Generation
# ──────────────────────────────────────────────────────────────────

with tab_video:
    st.header("Video Generation")

    # Model selector (index-based — no fragile name matching)
    video_idx = st.selectbox(
        "Choose a model",
        range(len(VIDEO_MODELS)),
        format_func=lambda i: VIDEO_MODELS[i].display_name,
        key="video_model",
    )
    model = VIDEO_MODELS[video_idx]

    st.divider()

    # Render form
    kwargs = _render_generation_form(model)

    if kwargs is not None:
        # ── Validate parameters against live Replicate schema ─────
        try:
            from src.validation import validate_params
            validate_params(model, kwargs)
        except Exception as exc:
            st.error(f"Invalid parameters:\n\n{exc}")
            st.stop()

        with st.status(
            f"Generating with {model.display_name}…",
            expanded=True,
        ) as status:
            try:
                from src import video_gen as vg

                uploaded = kwargs.pop("_uploaded_image", None)
                if uploaded and model.supports_image:
                    uploaded.seek(0)
                    kwargs["image"] = uploaded

                start_time = monotonic()
                progress_line = st.empty()

                def progress_callback(event: str, prediction: object) -> None:
                    elapsed = format_duration(monotonic() - start_time)
                    pred_id = getattr(prediction, "id", "")
                    pred_status = getattr(prediction, "status", event)
                    progress_line.write(
                        f"Replicate status: `{pred_status}` · elapsed {elapsed}"
                        + (f" · prediction `{pred_id}`" if pred_id else "")
                    )

                kwargs["progress_callback"] = progress_callback

                if model.name == "wan-2.7-t2v":
                    result = vg.generate_wan_2_7_t2v(**kwargs)
                elif model.name == "wan-2.5-i2v-fast":
                    result = vg.generate_wan_2_5_i2v(**kwargs)
                elif model.name == "seedance-2.0":
                    result = vg.generate_seedance_2_0(**kwargs)
                else:
                    st.error(f"Unknown model: {model.name}")
                    result = None

                if result is None:
                    status.update(label="Generation cancelled", state="error")
                elif result["success"]:
                    status.update(label="Generation complete! 🎉", state="complete")
                    st.toast("Video generated successfully! 🎉")
                    st.success(f"Done in {format_duration(result['predict_time'])}")
                    st.video(result["url"])

                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        st.link_button("Open / download video", result["url"])
                    with col_b:
                        st.metric(
                            "⏱ Predict Time",
                            format_duration(result["predict_time"]),
                        )
                    with col_c:
                        st.metric(
                            "💰 Estimated Cost",
                            format_cost(result.get("estimated_cost", 0)),
                        )
                    if result.get("prediction_url"):
                        st.caption(f"Replicate prediction: {result['prediction_url']}")
                    st.caption(
                        "Output URLs are hosted by Replicate and expire after ~1 hour."
                    )
                else:
                    status.update(label="Generation failed", state="error")
                    st.error(f"Error: {result['error']}")
                    if result.get("prediction_url"):
                        st.caption(f"Replicate prediction: {result['prediction_url']}")
                    st.toast("Generation failed ❌")

            except Exception as exc:
                status.update(label="Generation error", state="error")
                st.error(f"Unexpected error: {exc}")
                st.toast("Error during generation")


# ──────────────────────────────────────────────────────────────────
#  TAB: 3D Generation
# ──────────────────────────────────────────────────────────────────

with tab_3d:
    st.header("3D Generation")

    # Model selector (index-based)
    threed_idx = st.selectbox(
        "Choose a model",
        range(len(THREED_MODELS)),
        format_func=lambda i: THREED_MODELS[i].display_name,
        key="3d_model",
    )
    model_3d = THREED_MODELS[threed_idx]

    st.divider()

    kwargs_3d = _render_generation_form(model_3d)

    if kwargs_3d is not None:
        # ── Validate parameters against live Replicate schema ─────
        try:
            from src.validation import validate_params
            validate_params(model_3d, kwargs_3d)
        except Exception as exc:
            st.error(f"Invalid parameters:\n\n{exc}")
            st.stop()

        with st.status(
            f"Generating with {model_3d.display_name}…",
            expanded=True,
        ) as status:
            try:
                from src import threed_gen as tg

                uploaded = kwargs_3d.pop("_uploaded_image", None)
                if uploaded and model_3d.supports_image:
                    uploaded.seek(0)
                    kwargs_3d["image"] = uploaded

                start_time = monotonic()
                progress_line = st.empty()

                def progress_callback(event: str, prediction: object) -> None:
                    elapsed = format_duration(monotonic() - start_time)
                    pred_id = getattr(prediction, "id", "")
                    pred_status = getattr(prediction, "status", event)
                    progress_line.write(
                        f"Replicate status: `{pred_status}` · elapsed {elapsed}"
                        + (f" · prediction `{pred_id}`" if pred_id else "")
                    )

                kwargs_3d["progress_callback"] = progress_callback

                if model_3d.name == "hunyuan3d-2":
                    result = tg.generate_hunyuan3d_2(**kwargs_3d)
                elif model_3d.name == "trellis-2":
                    result = tg.generate_trellis_2(**kwargs_3d)
                else:
                    st.error(f"Unknown model: {model_3d.name}")
                    result = None

                if result is None:
                    status.update(label="Generation cancelled", state="error")
                elif result["success"]:
                    status.update(label="Generation complete! 🎉", state="complete")
                    st.toast("3D model generated successfully! 🎉")
                    model_url = result.get("model_url") or result.get("mesh_url", "")

                    if model_url:
                        viewer_html = f"""
                        <model-viewer
                            src="{model_url}"
                            alt="Generated 3D model"
                            auto-rotate
                            camera-controls
                            style="width:100%; height:500px; background:#1a1a2e;
                                   border-radius:8px;">
                        </model-viewer>
                        <script type="module"
                            src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.5.0/model-viewer.min.js">
                        </script>
                        """
                        st.components.v1.html(viewer_html, height=520)

                    video_url = result.get("video_url", "")
                    if video_url:
                        st.caption("Rendered preview:")
                        st.video(video_url)

                    col_a, col_b, col_c = st.columns(3)
                    with col_a:
                        if model_url:
                            st.link_button("Open / download 3D model", model_url)
                    with col_b:
                        st.metric(
                            "⏱ Predict Time",
                            format_duration(result["predict_time"]),
                        )
                    with col_c:
                        st.metric(
                            "💰 Estimated Cost",
                            format_cost(result.get("estimated_cost", 0)),
                        )
                    if result.get("prediction_url"):
                        st.caption(f"Replicate prediction: {result['prediction_url']}")
                    st.caption(
                        "Output URLs are hosted by Replicate and expire after ~1 hour."
                    )
                else:
                    status.update(label="Generation failed", state="error")
                    st.error(f"Error: {result['error']}")
                    if result.get("prediction_url"):
                        st.caption(f"Replicate prediction: {result['prediction_url']}")
                    st.toast("Generation failed ❌")

            except Exception as exc:
                status.update(label="Generation error", state="error")
                st.error(f"Unexpected error: {exc}")
                st.toast("Error during generation")


# ──────────────────────────────────────────────────────────────────
#  TAB: History
# ──────────────────────────────────────────────────────────────────

with tab_history:
    st.header("Generation History")

    # ── Summary cards ──
    st.subheader("Summary")
    total_stats = get_total_stats()

    if total_stats and total_stats[0] and total_stats[0] > 0:
        c1, c2, c3 = st.columns(3)
        with c1:
            st.metric("Total Generations", total_stats[0])
        with c2:
            st.metric("Total Cost", format_cost(total_stats[1] or 0))
        with c3:
            st.metric("Avg Predict Time", format_duration(total_stats[2] or 0))
    else:
        st.info("No generations yet. Create your first video or 3D model!")

    # ── Per-model breakdown ──
    st.subheader("By Model")
    model_stats = get_stats_by_model()
    if model_stats:
        for row in model_stats:
            name, count, total_cost, avg_time = row
            with st.expander(f"{name} ({count} generation{'s' if count != 1 else ''})"):
                mc1, mc2 = st.columns(2)
                with mc1:
                    st.metric("Total Cost", format_cost(total_cost or 0))
                with mc2:
                    st.metric("Avg Time", format_duration(avg_time or 0))

    # ── Full history table ──
    st.subheader("Recent Generations")
    st.caption(
        "Replicate delivery URLs are temporary and usually expire after ~1 hour."
    )
    rows = get_all_generations(limit=50)

    if rows:
        import pandas as pd

        df = pd.DataFrame(
            rows,
            columns=[
                "ID",
                "Model",
                "Type",
                "Timestamp",
                "Prompt",
                "Input Image",
                "Params",
                "URL",
                "Predict Time (s)",
                "Total Time (s)",
                "Est. Cost (USD)",
                "Duration (s)",
                "Status",
            ],
        )

        model_filter = st.multiselect(
            "Filter by model",
            sorted(df["Model"].dropna().unique()),
            default=sorted(df["Model"].dropna().unique()),
        )
        search = st.text_input(
            "Search prompts",
            placeholder="camera move, robot, castle…",
        )
        filtered = df[df["Model"].isin(model_filter)] if model_filter else df
        if search:
            filtered = filtered[
                filtered["Prompt"].fillna("").str.contains(search, case=False)
            ]

        display = filtered[
            [
                "Timestamp",
                "Model",
                "Type",
                "Prompt",
                "URL",
                "Predict Time (s)",
                "Est. Cost (USD)",
                "Status",
            ]
        ].copy()
        display["Timestamp"] = display["Timestamp"].apply(format_timestamp)
        display["Predict Time (s)"] = display["Predict Time (s)"].apply(
            lambda x: format_duration(x) if x else "—"
        )
        display["Est. Cost (USD)"] = display["Est. Cost (USD)"].apply(
            lambda x: format_cost(x) if x else "—"
        )
        display["Output"] = display["URL"]
        display = display.drop(columns=["URL"])

        st.dataframe(
            display,
            use_container_width=True,
            hide_index=True,
            column_config={
                "Output": st.column_config.LinkColumn(
                    "Output",
                    display_text="Open",
                    help="Temporary Replicate URL; may expire after about one hour.",
                )
            },
        )
    else:
        st.info("No history available yet.")
