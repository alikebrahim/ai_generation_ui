# AI Generation UI

A Streamlit-based interface for video and 3D generation using Replicate API today. fal.ai development is intentionally deferred until after the v1.0.0 Replicate-only baseline.

**Current version**: v0.6.10 — Eleven Replicate video models + seven 3D/texture models, workflow-aware Video tab, dry-run previews.

## Purpose

This project provides a clean, simple web interface for:

- **Video** (3 models): Wan 2.7 T2V, Wan 2.5 I2V Fast, Seedance 2.0
- **3D / texture** (7 models): Hunyuan3D 2.0, Hunyuan3D 2 Multiview, TRELLIS 2,
  Hunyuan 3D 3.1, Text2Tex, Adirik Texture, Rodin Gen-2

Workflows include text-to-video, image-to-video, image-to-3D, text-to-3D,
multiview-to-3D, and mesh texturing — all via Replicate today.

Image generation is handled separately via ComfyUI workflows (not in this project).

## Provider Direction

Current implemented provider support is Replicate. fal.ai is not part of the v0.x implementation plan or the v1.0.0 release target;
it begins after the Replicate-only personal workflow is stable.
The intended user flow remains workflow-first: choose Video or 3D, pick a model
by practical outcome/use case, then see the provider as secondary context for
setup, pricing, status, and troubleshooting.

v0.4.3–v0.5.10 completed UI stabilization (focused panels, gallery-first History).
v0.6.0 added **Preview request (no charge)**, shared payload builders, and schema
diagnostics. v0.6.5 expanded the 3D catalogue with multiview and mesh-texturing
models plus mesh/multiview file uploads in the form.

Future fal.ai/provider-aware design details are documented in
`IMPLEMENTATION_PLAN_PROVIDER_EXPANSION.md` and scheduled after v1.0.0 in
`ROADMAP.md`. The pre-v1 architecture refactor is documented in
`IMPLEMENTATION_PLAN_ARCHITECTURE_REFACTOR.md`.

## Why This Project?

The `comfyui-replicate` custom node doesn't support video or 3D outputs because these models return complex file types (video files, 3D meshes) rather than simple images or text. This project fills that gap by:

1. Calling provider APIs directly via Python, currently Replicate only
2. Displaying video with Streamlit's built-in `st.video()` component
3. Displaying 3D models using Google's `<model-viewer>` web component
4. Providing a unified interface for comparing different models/providers

## Architecture

```
┌─────────────────────────────────────┐
│   Streamlit Web Interface           │
│  (page navigation, input forms,     │
│   model selection, video/3D preview)│
└──────────────┬──────────────────────┘
               │
               │ Python API calls
               │
┌──────────────▼──────────────────────┐
│   Generation / Provider Services    │
│  Current behavior: Replicate         │
│  v0.6.x: dry-run + payload builders │
│  fal.ai: post-v1.0 planned         │
└──────────────┬──────────────────────┘
               │
               │ Returns provider URLs
               │ App saves local copies
               │
┌──────────────▼──────────────────────┐
│   Inline Preview + Local History    │
│  (st.video(url), model-viewer)      │
│   Local files under outputs/        │
└─────────────────────────────────────┘
```

## Tech Stack

- **Package Manager**: uv (fast, modern Python project management)
- **Frontend**: Streamlit 1.58.0 (Python web framework)
- **API Providers**: Replicate 1.0.7 today; fal.ai planned post-v1.0 via provider adapter
- **Video Display**: Streamlit's built-in `st.video()`
- **3D Display**: Google's `<model-viewer>` (via Streamlit custom HTML)
- **Environment Variables**: python-dotenv 1.2.2
- **History**: SQLite database for generation metadata

## Quick Start

### Prerequisites

- Python 3.11+ (managed by uv)
- Replicate API token ([get one here](https://replicate.com/account/api-tokens))
- fal.ai API token is not needed for v0.x or v1.0.0; it will be needed only once post-v1.0 fal.ai support is implemented

### Installation

```bash
# Clone or navigate to project
cd ai_generation_ui

# Install uv (if not already installed)
curl -LsSf https://astral.sh/uv/install.sh | sh

# Create virtual environment
uv venv

# Activate it
source .venv/bin/activate

# Install the project and its dependencies (editable mode)
#   uv pip install -e .          — runtime deps only
#   uv pip install -e ".[dev]"   — runtime + dev deps (ruff, black)
uv pip install -e ".[dev]"

# Set up environment variables
cp .env.example .env
# Edit .env and add your REPLICATE_API_TOKEN
# fal.ai credentials will be added when post-v1.0 fal.ai support is implemented
```

### Running the App

```bash
# Make sure your virtual environment is active (see above)
# If starting a new terminal session:
#   source .venv/bin/activate
cd ai_generation_ui
source .venv/bin/activate

# Run Streamlit
streamlit run app.py
```

The app will open at http://localhost:8501

## Project Structure

```
ai_generation_ui/
├── app.py                  # Main Streamlit app
├── pyproject.toml          # Project configuration (uv/pip)
├── .env.example            # Environment variable template
├── src/
│   ├── config.py          # Environment loading, paths, constants
│   ├── pricing.py         # Static pricing table / cost estimates
│   ├── models_config.py   # Model IDs, provider metadata, param schemas
│   ├── cost_tracker.py    # Backward-compatible SQLite history API
│   ├── history_service.py # Provider-aware typed history service
│   ├── generation_service.py # UI entry point + dry-run / safety probes
│   ├── generation_registry.py # Model name → handler dispatch
│   ├── replicate_payload.py  # Shared Replicate input builders
│   ├── schema_diagnostics.py # Non-paid schema drift checks
│   ├── storage_service.py # Centralized local output downloads
│   ├── video_gen.py       # Replicate video workflow wrappers
│   ├── threed_gen.py      # Replicate 3D/texture workflow wrappers
│   ├── providers/         # Provider adapters; Replicate implemented
│   ├── ui/                # Streamlit tabs/forms/result views
│   └── utils.py           # Formatting, validation helpers, output utilities
├── data/
│   └── history.db         # SQLite database (auto-created)
├── outputs/              # Local copies of generated videos/3D models
│   ├── videos/
│   ├── models_3d/
│   └── thumbnails/
├── assets/               # Reserved for future static assets
├── scripts/
│   ├── model_diagnostics.py # Non-paid schema/registry probe (CLI)
│   └── paid_smoke.py        # Opt-in paid smoke (ALLOW_PAID_REPLICATE_SMOKE=1)
└── IMPLEMENTATION_PLAN.md # Original step-by-step build guide
```

Non-paid local checks:

```bash
uv run python scripts/model_diagnostics.py
```

The completed v0.4.x architecture refactor is documented in
`IMPLEMENTATION_PLAN_ARCHITECTURE_REFACTOR.md` and
`IMPLEMENTATION_VER-0.4.3-TO-0.4.9.md`.

## Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
REPLICATE_API_TOKEN=r8_your_token_here
# fal.ai token variable will be added for post-v1.0 fal.ai support
```

The app loads this automatically using python-dotenv.

## Status

**v0.6.10 personal local beta.** The app supports eleven video models and seven 3D/texture workflows on Replicate, with a workflow filter on the Video tab, gallery-first History, durable local outputs, and v0.6.x generation safety (preview request, payload builders, schema diagnostics).

This is intentionally a personal-use app rather than a production product. The
focus is a robust local UI/UX that avoids obvious invalid paid provider calls and
keeps useful generation history with local file persistence. It remains pre-1.0
because authorized live workflow smoke QA (v0.8.0) and plain-English UX for
non-technical users are still pending. fal.ai is deliberately deferred until after
the v1.0.0 Replicate-only baseline.

The next planned work is **v0.7.0** (errors, progress messaging, recovery). See
`ROADMAP.md`. Release **v0.6.10** added eight video models and workflow-aware Video
tab UI — see `IMPLEMENTATION_VER-0.6.10.md`. **Known limitations (post-1.0)**: multimodal
models use single-file reference uploads only; Aleph has no keyframe UI yet — see
`ROADMAP.md` “Advanced video inputs”.

See `ITER_1_IMPLEMENTATION.md` for the as-built reference,
`IMPLEMENTATION_VER-0.4.3-TO-0.4.9.md` for the completed v0.4.x refactor,
`IMPLEMENTATION_VER-0.5.0-TO-0.5.10.md` for the completed v0.5 UI/UX pass,
`IMPLEMENTATION_VER-0.6.0.md` for the v0.6.0 safety/dry-run pass,
`IMPLEMENTATION_VER-0.6.5.md` for the v0.6.5 3D/texture expansion,
`IMPLEMENTATION_VER-0.6.10.md` for the v0.6.10 video expansion and UI plan,
`IMPLEMENTATION_PLAN_PROVIDER_EXPANSION.md` for the v1.0.0+ Replicate + fal.ai
provider plan, and `ROADMAP.md` for the versioned plan toward v1.0.0 and post-v1.0 provider expansion.
