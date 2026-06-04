#!/usr/bin/env python3
"""Run non-paid model schema diagnostics (optional remote Replicate fetch).

Usage:
    uv run python scripts/model_diagnostics.py
    uv run python scripts/model_diagnostics.py --no-remote
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))  # noqa: E402

from dotenv import load_dotenv  # noqa: E402

from src.generation_registry import verify_all_models_have_handlers  # noqa: E402
from src.generation_service import run_local_safety_checks  # noqa: E402
from src.schema_diagnostics import (  # noqa: E402
    format_report_text,
    run_all_diagnostics,
    validate_presets,
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Model schema diagnostics (no paid calls)"
    )
    parser.add_argument(
        "--no-remote",
        action="store_true",
        help="Skip Replicate API schema fetch; local config checks only",
    )
    args = parser.parse_args()

    load_dotenv(ROOT / ".env")

    print("Registry handlers…")
    if not verify_all_models_have_handlers():
        print("FAIL: missing generation handlers")
        return 1
    print("OK")

    print("\nSchema diagnostics…")
    reports = run_all_diagnostics(fetch_remote=not args.no_remote)
    exit_code = 0
    for report in reports:
        print(format_report_text(report))
        print()
        if not report.ok:
            exit_code = 1

    print("Payload preparation probes…")
    safety = run_local_safety_checks()
    if not safety["validation_ok"]:
        print("FAIL: validation probes")
        for err in safety["validation_errors"]:
            print(f"  {err}")
        exit_code = 1
    else:
        print("OK")

    print("\nPreset constraint probes…")
    preset_errors = validate_presets()
    if preset_errors:
        print("FAIL: invalid preset values")
        for err in preset_errors:
            print(f"  {err}")
        exit_code = 1
    else:
        print("OK")

    if not safety["schema_ok"]:
        print("FAIL: schema comparison reported errors")
        exit_code = 1
    elif exit_code == 0:
        print("\nAll non-paid diagnostics passed.")

    return exit_code


if __name__ == "__main__":
    raise SystemExit(main())
