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

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)
ASSETS_DIR.mkdir(parents=True, exist_ok=True)

# --- Database ---
HISTORY_DB = DATA_DIR / "history.db"

# --- Polling intervals (seconds) ---
POLL_INTERVAL_VIDEO = 5
POLL_INTERVAL_3D = 10

# --- Retries ---
MAX_RETRIES = 3
