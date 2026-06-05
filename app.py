"""AI Generation Studio — Streamlit app for Replicate-powered video & 3D generation.

Usage:
    cd ai_generation_ui
    uv run streamlit run app.py
"""

from __future__ import annotations

import sys
from importlib import reload
from pathlib import Path

# Allow imports from src/ without installing the package
sys.path.insert(0, str(Path(__file__).resolve().parent))

import streamlit as st

from src import utils as app_utils
from src.config import check_token
from src.cost_tracker import init_db
from src.ui.audio_tab import render_audio_tab
from src.ui.history_tab import render_history_tab
from src.ui.style import inject_app_style
from src.ui.threed_tab import render_3d_tab
from src.ui.video_tab import render_video_tab

if not hasattr(app_utils, "friendly_error_message"):
    # Streamlit reruns app.py in the same Python process. If src.utils was
    # imported before a helper was added, the old module object can remain in
    # sys.modules and make `from src.utils import friendly_error_message` fail
    # until the server is restarted. Reload once so hot-reload recovers cleanly.
    app_utils = reload(app_utils)

st.set_page_config(
    page_title="AI Generation Studio",
    page_icon="🎬",
    layout="wide",
)

inject_app_style()

try:
    check_token()
except RuntimeError as err:
    st.error(str(err))
    st.stop()

init_db()

st.title("🎬 AI Generation Studio")
st.caption(
    "A personal Streamlit workspace for videos, 3D models, audio, and history."
)

if hasattr(st, "divider"):
    st.divider()

# ═══════════════════════════════════════════════════════════════════
#  PAGE NAVIGATION
# ═══════════════════════════════════════════════════════════════════

PAGE_LABELS = {
    "video": "🎥 Video",
    "3d": "🧊 3D",
    "audio": "🎵 Audio",
    "history": "📊 History",
}
LABEL_TO_PAGE = {label: page for page, label in PAGE_LABELS.items()}

raw_page = st.query_params.get("page", "video")
if isinstance(raw_page, list):
    raw_page = raw_page[0] if raw_page else "video"
active_page = raw_page if raw_page in PAGE_LABELS else "video"

selected_label = st.segmented_control(
    "Main page",
    options=list(PAGE_LABELS.values()),
    default=PAGE_LABELS[active_page],
    label_visibility="collapsed",
)
selected_page = LABEL_TO_PAGE.get(
    selected_label or PAGE_LABELS[active_page], active_page
)
if selected_page != active_page:
    st.query_params["page"] = selected_page
    st.rerun()

if selected_page == "video":
    render_video_tab()
elif selected_page == "3d":
    render_3d_tab()
elif selected_page == "audio":
    render_audio_tab()
else:
    render_history_tab()
