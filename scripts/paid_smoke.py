#!/usr/bin/env python3
"""Optional paid Replicate smoke tests — explicit opt-in only.

Requires:
    ALLOW_PAID_REPLICATE_SMOKE=1
    REPLICATE_API_TOKEN in .env

Usage:
    ALLOW_PAID_REPLICATE_SMOKE=1 uv run python scripts/paid_smoke.py --workflow t2v
    ALLOW_PAID_REPLICATE_SMOKE=1 uv run python scripts/paid_smoke.py \\
        --workflow i2v --image path.png
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from dotenv import load_dotenv  # noqa: E402

WORKFLOWS = {
    "t2v": ("wan-2.7-t2v", {"prompt": "A red ball rolling on a table, cinematic"}),
    "i2v": ("wan-2.5-i2v-fast", {"prompt": "Gentle camera push-in"}),
    "i23d": ("hunyuan3d-2", {}),
    "t23d": ("hunyuan-3d-3.1", {"prompt": "A small wooden chair"}),
}


def _require_opt_in() -> None:
    if os.getenv("ALLOW_PAID_REPLICATE_SMOKE") != "1":
        print(
            "Refusing paid smoke: set ALLOW_PAID_REPLICATE_SMOKE=1 "
            "with explicit authorization.",
            file=sys.stderr,
        )
        raise SystemExit(2)


def _run_smoke(model_name: str, params: dict[str, Any]) -> int:
    from src.generation_service import get_generation_service

    print(f"Running PAID smoke → {model_name}")
    print("Ctrl+C to abort before the call completes if this was a mistake.")

    preview = get_generation_service().prepare_generation_request(model_name, **params)
    if not preview.get("ok"):
        print("Dry-run validation failed:", preview, file=sys.stderr)
        return 1
    print("Dry-run OK:", preview.get("summary_lines"))

    result = get_generation_service().generate(model_name, **params)
    if result.get("success"):
        print("SUCCESS:", result.get("url") or result.get("model_url") or result)
        return 0
    print("FAILED:", result.get("error"), file=sys.stderr)
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Authorized paid Replicate smoke test")
    parser.add_argument(
        "--workflow",
        choices=sorted(WORKFLOWS),
        required=True,
        help="Which workflow to smoke-test",
    )
    parser.add_argument(
        "--image",
        type=Path,
        help="Local image path for i2v / i23d workflows",
    )
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")
    _require_opt_in()

    if not os.getenv("REPLICATE_API_TOKEN"):
        print("REPLICATE_API_TOKEN is not set.", file=sys.stderr)
        return 2

    model_name, params = WORKFLOWS[args.workflow]
    params = dict(params)

    if args.workflow in {"i2v", "i23d"}:
        if not args.image or not args.image.is_file():
            print("--image PATH is required for this workflow.", file=sys.stderr)
            return 2
        with args.image.open("rb") as image_file:
            params["image"] = image_file
            return _run_smoke(model_name, params)

    return _run_smoke(model_name, params)


if __name__ == "__main__":
    raise SystemExit(main())
