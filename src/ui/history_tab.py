"""History tab for Streamlit app."""

from __future__ import annotations

import base64
import json
import shutil
import subprocess
from pathlib import Path
from typing import cast
from urllib.parse import quote

import pandas as pd
import streamlit as st
import streamlit.components.v1 as components

from src import utils as app_utils
from src.cost_tracker import (
    get_all_generations,
    get_stats_by_model,
    get_total_stats,
    update_generation_thumbnail,
)
from src.storage_service import get_storage_service

format_cost = app_utils.format_cost
format_duration = app_utils.format_duration
format_timestamp = app_utils.format_timestamp

HISTORY_COLUMNS = [
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
    "Mode",
    "Status",
    "Local File",
    "Thumbnail",
    "File Size (B)",
    "Provider",
    "Provider Model ID",
    "Provider Job ID",
    "Provider Job URL",
    "Output Assets",
]


def mime_for_path(path: Path) -> str:
    """Best-effort MIME type for Streamlit local download buttons."""
    suffix = path.suffix.lower()
    return {
        ".mp4": "video/mp4",
        ".webm": "video/webm",
        ".mov": "video/quicktime",
        ".glb": "model/gltf-binary",
        ".gltf": "model/gltf+json",
        ".obj": "text/plain",
        ".png": "image/png",
        ".jpg": "image/jpeg",
        ".jpeg": "image/jpeg",
    }.get(suffix, "application/octet-stream")


def safe_local_path(value: object) -> Path | None:
    """Return an existing local path from history, or None if unavailable."""
    if not value or not isinstance(value, str):
        return None
    path = Path(value)
    return path if path.exists() and path.is_file() else None


def _preview_generation_id() -> int | None:
    """Return the gallery row selected for inline preview, if any."""
    raw_value = st.query_params.get("preview_generation_id")
    if isinstance(raw_value, list):
        raw_value = raw_value[0] if raw_value else None
    try:
        return int(raw_value) if raw_value else None
    except (TypeError, ValueError):
        return None


def _open_in_file_finder(path: Path) -> bool:
    """Open the local file's folder in the desktop file finder."""
    commands = [
        ["nautilus", "--select", str(path)],
        ["dolphin", "--select", str(path)],
        ["nemo", str(path.parent)],
        ["thunar", str(path.parent)],
        ["gio", "open", str(path.parent)],
        ["xdg-open", str(path.parent)],
    ]
    for command in commands:
        if not shutil.which(command[0]):
            continue
        try:
            subprocess.Popen(  # noqa: S603 - local desktop file reveal only
                command,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
            )
            return True
        except OSError:
            continue
    return False


def _row_prompt(value: object) -> str:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return "No prompt provided"


def _row_assets_summary(value: object) -> str:
    if not value or not isinstance(value, str):
        return "—"
    try:
        assets = json.loads(value)
    except json.JSONDecodeError:
        return "—"
    if not isinstance(assets, list) or not assets:
        return "—"
    kinds = [
        str(asset.get("kind", "asset")) for asset in assets if isinstance(asset, dict)
    ]
    return ", ".join(kinds) if kinds else "—"


def _trigger_remix(row: pd.Series) -> None:
    """Store remix intent in session and navigate to the matching tab."""
    model_name = str(row.get("Model") or "")
    model_type = str(row.get("Type") or "video").lower()
    prompt_val = row.get("Prompt") or ""
    if prompt_val == "No prompt provided":
        prompt_val = ""
    params_raw = row.get("Params") or "{}"
    try:
        params = (
            json.loads(params_raw)
            if isinstance(params_raw, str)
            else (params_raw or {})
        )
    except Exception:
        params = {}
    # Keep only scalar params we can safely prefill (files will need re-upload)
    safe_params = {}
    for k, v in params.items() if isinstance(params, dict) else []:
        if k in ("prompt", "image", "video", "obj_file", "shape_path"):
            continue
        if isinstance(v, (str, int, float, bool)) or v is None:
            safe_params[k] = v
    st.session_state["pending_remix"] = {
        "model_name": model_name,
        "model_type": model_type,
        "prompt": prompt_val,
        "params": safe_params,
    }
    if model_type == "audio":
        target = "audio"
    elif model_type == "image":
        target = "image"
    elif model_type == "video":
        target = "video"
    else:
        target = "3d"
    st.query_params["page"] = target
    st.rerun()


def _image_data_uri(path: Path) -> str | None:
    """Return a browser-safe data URI for a local thumbnail image."""
    try:
        data = base64.b64encode(path.read_bytes()).decode("ascii")
    except OSError:
        return None
    return f"data:{mime_for_path(path)};base64,{data}"


def _select_gallery_preview(row_id: int) -> None:
    """Select a gallery row for inline preview without leaving History."""
    st.query_params["page"] = "history"
    st.query_params["preview_generation_id"] = str(row_id)
    st.rerun()


def _render_clickable_thumbnail(row: pd.Series, thumbnail_path: Path) -> None:
    """Render thumbnail + compact preview action."""
    row_id = int(str(row["ID"]))
    st.image(str(thumbnail_path), width="stretch", caption="Thumbnail")
    if st.button(
        "🔍 Preview",
        key=f"preview_thumb_{row_id}",
        help=f"Show larger preview + details for generation {row_id}",
        use_container_width=False,
    ):
        _select_gallery_preview(row_id)


def _render_gallery_preview(row: pd.Series) -> None:
    """Render the selected gallery item in an inline preview area."""
    local_path = safe_local_path(row.get("Local File"))
    url = row.get("URL", "")
    model_type = row.get("Type", "")
    source = str(local_path) if local_path is not None else str(url or "")

    st.markdown('<span id="gallery-preview"></span>', unsafe_allow_html=True)
    with st.container(border=True):
        st.markdown(f"#### Preview: {row['Model']}")
        st.caption(
            f"{row.get('Mode', model_type)} · {format_timestamp(str(row['Timestamp']))}"
        )
        if model_type == "video" and source:
            st.video(source)
        elif model_type == "audio" and source:
            st.audio(source)
        elif model_type == "image" and source:
            st.image(source, use_container_width=True)
        elif model_type == "3d" and source:
            safe_url = quote(source, safe=":/?&=#%+-_.,~")
            viewer_html = f"""
            <model-viewer
                src="{safe_url}"
                alt="Generated 3D model"
                auto-rotate
                camera-controls
                style="width:100%; height:420px; background:#1a1a2e;
                       border-radius:0.85rem;">
            </model-viewer>
            <script type="module"
                src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.5.0/model-viewer.min.js">
            </script>
            """
            components.html(viewer_html, height=440)
        else:
            st.info("No previewable local file or provider URL is available.")

        controls = st.columns([1, 1, 2])
        with controls[0]:
            if local_path is not None:
                if st.button(
                    "Open in file finder",
                    key=f"preview_reveal_{row['ID']}",
                    use_container_width=True,
                ):
                    if _open_in_file_finder(local_path):
                        st.toast("Opened file location.")
                    else:
                        st.warning("Could not find a desktop file finder to open.")
        with controls[1]:
            if st.button(
                "Close preview",
                key=f"preview_close_{row['ID']}",
                use_container_width=True,
            ):
                st.query_params.pop("preview_generation_id", None)
                st.rerun()


def _records_dataframe(rows: list[tuple]) -> pd.DataFrame:
    return pd.DataFrame(rows, columns=HISTORY_COLUMNS)


def _backfill_missing_video_thumbnails(rows: list[tuple]) -> bool:
    """Create thumbnails for existing local video rows that predate v0.5.5."""
    changed = False
    storage = get_storage_service()
    for row in rows:
        record = dict(zip(HISTORY_COLUMNS, row, strict=True))
        if record.get("Type") != "video" or record.get("Thumbnail"):
            continue
        local_path = safe_local_path(record.get("Local File"))
        if local_path is None:
            continue
        thumbnail_path = storage.ensure_video_thumbnail(local_path)
        if thumbnail_path is not None:
            update_generation_thumbnail(int(record["ID"]), str(thumbnail_path))
            changed = True
    return changed


def _apply_filters(df: pd.DataFrame) -> pd.DataFrame:
    type_options = sorted(df["Type"].dropna().astype(str).unique())
    model_options = sorted(df["Model"].dropna().astype(str).unique())
    provider_options = sorted(df["Provider"].dropna().astype(str).unique())
    status_options = sorted(df["Status"].dropna().astype(str).unique())

    # 5 filters (search + type + model + provider + status); early for browsing
    filter_col_1, filter_col_2, filter_col_3, filter_col_4, filter_col_5 = st.columns(
        [1.6, 0.9, 1.2, 1.0, 1.0]
    )
    with filter_col_1:
        search = st.text_input(
            "Search prompts", placeholder="camera move, robot, castle…"
        )
    with filter_col_2:
        type_filter = st.multiselect("Type", type_options, default=type_options)
    with filter_col_3:
        model_filter = st.multiselect("Model", model_options, default=model_options)
    with filter_col_4:
        provider_filter = st.multiselect(
            "Provider", provider_options, default=provider_options
        )
    with filter_col_5:
        status_filter = st.multiselect("Status", status_options, default=status_options)

    filtered: pd.DataFrame = df.copy()
    if type_filter:
        filtered = cast(
            pd.DataFrame, filtered[filtered["Type"].astype(str).isin(type_filter)]
        )
    if model_filter:
        filtered = cast(
            pd.DataFrame, filtered[filtered["Model"].astype(str).isin(model_filter)]
        )
    if provider_filter:
        filtered = cast(
            pd.DataFrame,
            filtered[filtered["Provider"].astype(str).isin(provider_filter)],
        )
    if status_filter:
        filtered = cast(
            pd.DataFrame, filtered[filtered["Status"].astype(str).isin(status_filter)]
        )
    if search:
        filtered = cast(
            pd.DataFrame,
            filtered[
                filtered["Prompt"]
                .fillna("")
                .astype(str)
                .str.contains(search, case=False, regex=False)
            ],
        )
    return filtered


def _render_history_card(row: pd.Series) -> None:
    local_path_value = row.get("Local File")
    thumbnail_value = row.get("Thumbnail")
    local_path = safe_local_path(local_path_value)
    thumbnail_path = safe_local_path(thumbnail_value)
    has_local = local_path is not None
    has_missing_local = bool(local_path_value) and local_path is None
    url = row.get("URL", "")
    status_val = row.get("Status", "success")
    cost = row.get("Est. Cost (USD)", 0)
    model_type = row.get("Type", "")

    with st.container(border=True):
        if thumbnail_path is not None:
            _render_clickable_thumbnail(row, thumbnail_path)
        else:
            fallback_icon = {
                "video": "🎬",
                "3d": "🧊",
                "audio": "🎵",
            }.get(model_type, "📁")
            st.markdown(
                f"{fallback_icon} **"
                f"{model_type.upper() if model_type else 'Generation'}**"
            )

        if status_val == "failed":
            st.markdown("**❌ Failed**")
        elif status_val == "cancelled":
            st.markdown("**⏹ Cancelled**")
        else:
            st.markdown("**✅ Success**")

        st.markdown(f"**{row['Model']}**")
        st.caption(
            f"{row.get('Mode', row['Type'])} · {format_timestamp(row['Timestamp'])}"
        )
        st.caption(_row_prompt(row.get("Prompt")))

        with st.expander("View prompt & settings", expanded=False):
            prompt_text = _row_prompt(row.get("Prompt"))
            if st.button(
                "Show prompt", key=f"copy_prompt_{row['ID']}", use_container_width=True
            ):
                st.toast("Prompt shown below — select to copy")
                st.code(prompt_text, language="text")
            params_json = row.get("Params")
            if params_json:
                if st.button(
                    "Show settings (JSON)",
                    key=f"copy_settings_{row['ID']}",
                    use_container_width=True,
                ):
                    st.toast("Settings JSON shown below")
                    st.code(params_json, language="json")
            try:
                params = json.loads(params_json) if isinstance(params_json, str) else {}
                if isinstance(params, dict) and "seed" in params:
                    seed_val = params["seed"]
                    if st.button(
                        f"Show seed ({seed_val})",
                        key=f"copy_seed_{row['ID']}",
                        use_container_width=True,
                    ):
                        st.toast("Seed shown below")
                        st.code(str(seed_val))
            except Exception:
                pass

        st.metric(
            "Cost",
            format_cost(cost) if cost else "—",
            label_visibility="collapsed",
            help=f"Cost: {format_cost(cost) if cost else '—'}",
        )

        if has_local:
            st.markdown("💾 **Saved locally**")
            st.caption(str(local_path))
        elif has_missing_local:
            st.markdown("⚠️ **Local file missing**")
            st.caption(str(local_path_value))
        else:
            st.markdown("☁️ **Temporary link**")
            st.caption("Output URL may expire after about 1 hour.")

        assets_summary = _row_assets_summary(row.get("Output Assets"))
        if assets_summary != "—":
            st.caption(f"Assets: {assets_summary}")

        if has_local and local_path is not None:
            if st.button(
                "Open in file finder",
                key=f"reveal_{row['ID']}",
                use_container_width=True,
            ):
                if _open_in_file_finder(local_path):
                    st.toast("Opened file location.")
                else:
                    st.warning("Could not find a desktop file finder to open.")

            max_inline_download = 200 * 1024 * 1024
            if local_path.stat().st_size <= max_inline_download:
                st.download_button(
                    "Download local file",
                    data=local_path.read_bytes(),
                    file_name=local_path.name,
                    mime=mime_for_path(local_path),
                    use_container_width=True,
                    key=f"download_{row['ID']}",
                )
            else:
                st.caption("Large file — open it from the path above.")
        elif url:
            st.link_button("Open temporary URL", url, use_container_width=True)

        # Remix / load settings for creative iteration (v0.6.6)
        if status_val == "success":
            if st.button(
                "♻️ Load settings into tab (remix)",
                key=f"remix_{row['ID']}",
                use_container_width=True,
                help="Prefill prompt/params (re-upload images/videos).",
            ):
                _trigger_remix(row)


def _render_gallery_tab(filtered: pd.DataFrame, total_count: int) -> None:
    st.markdown("#### Gallery")
    st.caption("Default visual browsing view. Use the filters to narrow things down.")

    if filtered.empty:
        st.info("No generations match your current filters.")
        return

    visible_count = len(filtered)
    st.caption(f"Showing {visible_count} of {total_count} saved generations.")

    preview_id = _preview_generation_id()
    if preview_id is not None:
        selected = filtered[filtered["ID"].astype(int) == preview_id]
        if not selected.empty:
            _render_gallery_preview(selected.iloc[0])
        else:
            st.info("That preview is hidden by the current filters.")

    num_cols = min(4, visible_count)
    cards = st.columns(num_cols) if num_cols > 1 else [st.container()]
    for i, (_, row) in enumerate(filtered.iterrows()):
        with cards[i % num_cols]:
            _render_history_card(row)


def _render_records_tab(filtered: pd.DataFrame) -> None:
    st.markdown("#### Records")
    st.caption(
        "Table view with provider and asset metadata for troubleshooting and lookup."
    )

    if filtered.empty:
        st.info("No records match your current filters.")
        return

    display: pd.DataFrame = cast(
        pd.DataFrame,
        filtered[
            [
                "Timestamp",
                "Model",
                "Type",
                "Mode",
                "Provider",
                "Status",
                "Prompt",
                "URL",
                "Provider Job ID",
                "Provider Job URL",
                "Predict Time (s)",
                "Est. Cost (USD)",
                "Local File",
                "Thumbnail",
                "Output Assets",
            ]
        ].copy(),
    )
    display["Prompt"] = display["Prompt"].apply(_row_prompt)
    display["Timestamp"] = display["Timestamp"].apply(format_timestamp)
    display["Predict Time (s)"] = display["Predict Time (s)"].apply(
        lambda x: format_duration(x) if x else "—"
    )
    display["Est. Cost (USD)"] = display["Est. Cost (USD)"].apply(
        lambda x: format_cost(x) if x else "—"
    )
    display["Assets"] = display["Output Assets"].apply(_row_assets_summary)
    display = display.drop(columns=["Output Assets"])

    display["Availability"] = display.apply(
        lambda row: (
            "💾 Local"
            if safe_local_path(row["Local File"])
            else "⚠️ Missing local file"
            if row["Local File"]
            else "☁️ Temporary"
        ),
        axis=1,
    )
    display = display.drop(columns=["Local File", "Thumbnail"])

    st.dataframe(
        display,
        width="stretch",
        hide_index=True,
        column_config={
            "URL": st.column_config.LinkColumn(
                "Output",
                display_text="Open",
                help="Temporary Replicate URL; may expire after about one hour.",
            ),
            "Provider Job URL": st.column_config.LinkColumn(
                "Provider Job",
                display_text="Open",
                help="Open the provider job/prediction page when available.",
            ),
            "Assets": st.column_config.TextColumn(
                "Assets",
                help="Serialized asset kinds attached to the generation row.",
            ),
            "Availability": st.column_config.TextColumn(
                "Availability",
                help=(
                    "💾 = saved permanently on this machine; "
                    "☁️ = temporary provider link."
                ),
            ),
        },
    )


def render_history_tab() -> None:
    """Render the history tab."""
    st.header("Generation History")
    st.caption(
        "Gallery-first history with records, provider metadata, and "
        "local-file awareness."
    )

    gallery_limit = st.session_state.get("history_gallery_limit", 24)
    rows = get_all_generations(limit=gallery_limit)

    if rows and _backfill_missing_video_thumbnails(rows):
        rows = get_all_generations(limit=gallery_limit)

    # Fetch stats early (rendered at bottom in expander after gallery/filters)
    total_stats = get_total_stats()
    model_stats = get_stats_by_model()

    history_view = st.segmented_control(
        "History view",
        options=["Gallery", "Records"],
        default="Gallery",
        key="history_view",
        label_visibility="collapsed",
    )

    if not rows:
        st.info("No history available yet. Create your first generation!")
        return

    df = _records_dataframe(rows)
    filtered = _apply_filters(df)  # filters right after view (search/type/...)

    if history_view == "Gallery":
        _render_gallery_tab(filtered, len(df))
        if len(df) >= gallery_limit:
            more_col, _ = st.columns([1, 3])
            with more_col:
                if st.button("Load more history", use_container_width=True):
                    st.session_state["history_gallery_limit"] = gallery_limit + 24
                    st.rerun()
    else:
        _render_records_tab(filtered)

    # Usage stats at bottom (filters + gallery first)
    with st.expander("Usage stats", expanded=False):
        if total_stats and total_stats[0] and total_stats[0] > 0:
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("Total Generations", total_stats[0])
            with c2:
                st.metric("Total Cost", format_cost(total_stats[1] or 0))
            with c3:
                st.metric("Avg Predict Time", format_duration(total_stats[2] or 0))
        if model_stats:
            for row in model_stats:
                name, count, total_cost, avg_time = row
                with st.expander(f"{name} ({count} gen{'s' if count != 1 else ''})"):
                    mc1, mc2 = st.columns(2)
                    with mc1:
                        st.metric("Total Cost", format_cost(total_cost or 0))
                    with mc2:
                        st.metric("Avg Time", format_duration(avg_time or 0))
