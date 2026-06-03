# AI Generation UI

A Streamlit-based interface for video and 3D generation using Replicate API today. fal.ai development is intentionally deferred until v1.0.0 or later.

**Current version**: v0.4.2 — Hunyuan 3D 3.1 image upload patch.

## Purpose

This project provides a clean, simple web interface for:
- **Video generation**: Text-to-video (T2V), image-to-video (I2V)
- **3D generation**: Image-to-3D (I23D) and Hunyuan 3D 3.1 text-to-3D
  (T23D) via Replicate

Image generation is handled separately via ComfyUI workflows (not in this project).

## Provider Direction

Current implemented provider support is Replicate. fal.ai is not part of the v0.x
implementation plan; it begins at v1.0.0 or later, after the Replicate-only
personal workflow is stable.
The intended user flow remains workflow-first: choose Video or 3D, pick a model
by practical outcome/use case, then see the provider as secondary context for
setup, pricing, status, and troubleshooting.

Future fal.ai/provider-aware design details are documented in
`IMPLEMENTATION_PLAN_PROVIDER_EXPANSION.md` and scheduled from v1.0.0 in
`ROADMAP.md`.

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
│  (input forms, model selection,     │
│   video/3D preview)                 │
└──────────────┬──────────────────────┘
               │
               │ Python API calls
               │
┌──────────────▼──────────────────────┐
│   Provider Layer                   │
│  Current: Replicate                 │
│  fal.ai: v1.0.0+ planned            │
│  Workflows: Video + 3D              │
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
- **API Providers**: Replicate 1.0.7 today; fal.ai planned for v1.0.0+ via provider adapter
- **Video Display**: Streamlit's built-in `st.video()`
- **3D Display**: Google's `<model-viewer>` (via Streamlit custom HTML)
- **Environment Variables**: python-dotenv 1.2.2
- **History**: SQLite database for generation metadata

## Quick Start

### Prerequisites

- Python 3.11+ (managed by uv)
- Replicate API token ([get one here](https://replicate.com/account/api-tokens))
- fal.ai API token is not needed for v0.x; it will be needed only once v1.0.0+ fal.ai support is implemented

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
# fal.ai credentials will be added when v1.0.0+ fal.ai support is implemented
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
│   ├── pricing.py         # Static pricing table (hardware → $/sec)
│   ├── models_config.py   # Model IDs, param schemas (balanced/advanced)
│   ├── cost_tracker.py    # SQLite history (init, insert, query, stats)
│   ├── video_gen.py       # Current Replicate video wrappers
│   ├── threed_gen.py      # Current Replicate 3D wrappers
│   ├── providers/         # Future v1.0.0+ provider adapter layer
│   └── utils.py           # Helper functions (formatting, etc.)
├── data/
│   └── history.db         # SQLite database (auto-created)
├── outputs/              # Local copies of generated videos/3D models
│   ├── videos/
│   ├── models_3d/
│   └── thumbnails/
├── assets/
│   └── model_viewer.html  # Template for <model-viewer> HTML
└── IMPLEMENTATION_PLAN.md # Step-by-step build guide
```

## Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
REPLICATE_API_TOKEN=r8_your_token_here
# fal.ai token variable will be added for v1.0.0+ fal.ai support
```

The app loads this automatically using python-dotenv.

## Status

**v0.4.2 personal local beta.** Core UI, generation wrappers, cost/history
tracking, safer upload handling, Replicate output normalization, polling UX,
schema-driven controls, pre-submit validation, Hunyuan 3D 3.1 model with
text-to-3D/image-to-3D support, versioned Replicate calls for 3D models that
do not support versionless prediction endpoints, and durable local output
storage with a history card view are implemented. v0.4.2 specifically fixes
Hunyuan 3D 3.1 image uploads so valid JPG/PNG/WEBP files are sent with explicit
image MIME data URIs instead of extensionless provider file URLs.

This is intentionally a personal-use app rather than a production product. The
focus is a robust local UI/UX that avoids obvious invalid paid provider calls and
keeps useful generation history with local file persistence. It remains pre-1.0
because browser/live model QA is manual, plain-English UX for non-technical
users is pending, and generation safety/dry-run tooling is not yet implemented.
fal.ai is deliberately deferred until v1.0.0 or later.

See `ITER_1_IMPLEMENTATION.md` for the as-built reference,
`IMPLEMENTATION_PLAN_PROVIDER_EXPANSION.md` for the v1.0.0+ Replicate + fal.ai
provider plan, and `ROADMAP.md` for the versioned plan toward v1.0.0.
