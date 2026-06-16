"""Configuration and environment setup."""

import os
from pathlib import Path

from dotenv import load_dotenv

# Load .env from project root (one level above src/)
load_dotenv()

# --- API credentials ---
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")


def check_token() -> None:
    """Raise a user-friendly error if the Replicate token is missing."""
    if not REPLICATE_API_TOKEN:
        raise RuntimeError(
            "REPLICATE_API_TOKEN not found.\n\n"
            "1. Copy .env.example to .env:\n"
            "     cp .env.example .env\n"
            "2. Edit .env and add your token from https://replicate.com/account/api-tokens\n"
            "     REPLICATE_API_TOKEN=r8_your_token_here"
        )


# --- Project paths ---
PROJECT_ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ASSETS_DIR = PROJECT_ROOT / "assets"
OUTPUTS_DIR = PROJECT_ROOT / "outputs"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# --- Output subdirectories ---
OUTPUTS_VIDEOS_DIR = OUTPUTS_DIR / "videos"
OUTPUTS_MODELS_3D_DIR = OUTPUTS_DIR / "models_3d"
OUTPUTS_THUMBNAILS_DIR = OUTPUTS_DIR / "thumbnails"
OUTPUTS_AUDIO_DIR = OUTPUTS_DIR / "audio"
OUTPUTS_IMAGES_DIR = OUTPUTS_DIR / "images"
_OUTPUT_SUBDIRS = [
    OUTPUTS_VIDEOS_DIR,
    OUTPUTS_MODELS_3D_DIR,
    OUTPUTS_THUMBNAILS_DIR,
    OUTPUTS_AUDIO_DIR,
    OUTPUTS_IMAGES_DIR,
]
for _d in _OUTPUT_SUBDIRS:
    _d.mkdir(parents=True, exist_ok=True)

# --- Database ---
HISTORY_DB = DATA_DIR / "history.db"

# --- Polling intervals (seconds) ---
POLL_INTERVAL_VIDEO = 5
POLL_INTERVAL_3D = 10
POLL_INTERVAL_AUDIO = 5
POLL_INTERVAL_IMAGE = 5

# --- Retries ---
MAX_RETRIES = 3
