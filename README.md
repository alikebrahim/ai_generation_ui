# AI Generation UI

A Streamlit-based interface for video and 3D generation using Replicate API.

**Current version**: v0.2.0 — local beta / capability-safe baseline.

## Purpose

This project provides a clean, simple web interface for:
- **Video generation**: Text-to-video (T2V), image-to-video (I2V)
- **3D generation**: Image-to-3D (I23D); Text-to-3D is planned/future only
  when a reliable Replicate deployment is selected

Image generation is handled separately via ComfyUI workflows (not in this project).

## Why This Project?

The `comfyui-replicate` custom node doesn't support video or 3D outputs because these models return complex file types (video files, 3D meshes) rather than simple images or text. This project fills that gap by:

1. Calling Replicate API directly via Python
2. Displaying video with Streamlit's built-in `st.video()` component
3. Displaying 3D models using Google's `<model-viewer>` web component
4. Providing a unified interface for comparing different models

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
│   Replicate API                     │
│  Video: Wan 2.7 T2V, Wan 2.5 I2V,  │
│         Seedance 2.0                │
│  3D:    Hunyuan3D 2.0, TRELLIS 2   │
└──────────────┬──────────────────────┘
               │
               │ Returns ephemeral URLs
               │
┌──────────────▼──────────────────────┐
│   Inline Preview                    │
│  (st.video(url), model-viewer)      │
│   Download button on demand         │
└─────────────────────────────────────┘
```

## Tech Stack

- **Package Manager**: uv (fast, modern Python project management)
- **Frontend**: Streamlit 1.58.0 (Python web framework)
- **API**: Replicate 1.0.7 (official Python client)
- **Video Display**: Streamlit's built-in `st.video()`
- **3D Display**: Google's `<model-viewer>` (via Streamlit custom HTML)
- **Environment Variables**: python-dotenv 1.2.2
- **History**: SQLite database for generation metadata

## Quick Start

### Prerequisites

- Python 3.11+ (managed by uv)
- Replicate API token ([get one here](https://replicate.com/account/api-tokens))

### Installation

```bash
# Clone or navigate to project
cd /home/tima/ai_generation_ui

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
```

### Running the App

```bash
# Make sure your virtual environment is active (see above)
# If starting a new terminal session:
#   source .venv/bin/activate
cd /home/tima/ai_generation_ui
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
│   ├── video_gen.py       # Wan 2.7 T2V, Wan 2.5 I2V, Seedance 2.0
│   ├── threed_gen.py      # Hunyuan3D 2.0, TRELLIS 2
│   └── utils.py           # Helper functions (formatting, etc.)
├── data/
│   └── history.db         # SQLite database (auto-created)
├── assets/
│   └── model_viewer.html  # Template for <model-viewer> HTML
└── IMPLEMENTATION_PLAN.md # Step-by-step build guide
```

## Environment Variables

Create a `.env` file (copy from `.env.example`):

```bash
REPLICATE_API_TOKEN=r8_your_token_here
```

The app loads this automatically using python-dotenv.

## Status

**v0.2.0 local beta.** Core UI, generation wrappers, cost/history tracking,
safer upload handling, Replicate output normalization, and polling UX are implemented.

Still pre-1.0 because live paid generation smoke tests, browser visual QA, durable
output storage, and richer schema-driven model capability validation are not complete yet.

See `ITER_1_IMPLEMENTATION.md` for the as-built reference and `ROADMAP.md` for the versioned plan toward v1.0.0.
