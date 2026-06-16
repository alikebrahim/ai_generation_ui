"""Non-paid schema and metadata diagnostics for configured Replicate models."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

from src.models_config import (
    ALL_MODELS,
    ModelConfig,
    get_options_for_param,
    get_range_for_param,
)


@dataclass
class DiagnosticIssue:
    """One schema/metadata mismatch or warning."""

    severity: str  # "error", "warning", "info"
    code: str
    message: str


@dataclass
class ModelDiagnosticReport:
    """Diagnostics for one configured model."""

    model_name: str
    replicate_id: str
    issues: list[DiagnosticIssue] = field(default_factory=list)
    remote_fetched: bool = False
    remote_required: list[str] = field(default_factory=list)
    remote_properties: list[str] = field(default_factory=list)

    @property
    def ok(self) -> bool:
        return not any(i.severity == "error" for i in self.issues)


def _resolve_enum(prop: dict[str, Any]) -> list[Any] | None:
    if "enum" in prop:
        return list(prop["enum"])
    for container in ("allOf", "anyOf"):
        for item in prop.get(container, []):
            if isinstance(item, dict) and "enum" in item:
                return list(item["enum"])
    return None


def _resolve_min_max(prop: dict[str, Any]) -> tuple[Any | None, Any | None]:
    mn = prop.get("minimum")
    mx = prop.get("maximum")
    if mn is not None or mx is not None:
        return mn, mx
    for container in ("allOf", "anyOf"):
        for item in prop.get(container, []):
            if isinstance(item, dict):
                if item.get("minimum") is not None:
                    mn = item["minimum"]
                if item.get("maximum") is not None:
                    mx = item["maximum"]
    return mn, mx


def fetch_remote_input_schema(replicate_id: str) -> dict[str, Any] | None:
    """Fetch latest Replicate OpenAPI Input properties (requires API token)."""
    if not os.getenv("REPLICATE_API_TOKEN"):
        return None
    try:
        import replicate
    except ImportError:
        return None

    model = replicate.models.get(replicate_id)
    schema = model.latest_version.openapi_schema or {}
    inp = schema.get("components", {}).get("schemas", {}).get("Input", {})
    return {
        "required": list(inp.get("required", [])),
        "properties": inp.get("properties", {}),
        "latest_version_id": model.latest_version.id,
        "replicate_url": getattr(model, "url", f"https://replicate.com/{replicate_id}"),
    }


def _configured_param_names(model: ModelConfig) -> set[str]:
    names = (
        set(model.balanced_params) | set(model.advanced_params) | set(model.defaults)
    )
    names.discard("prompt")
    return names


def audit_capability_ui_config(model: ModelConfig) -> list[DiagnosticIssue]:
    """Detect multimodal media params registered in multiple UI surfaces."""
    from src.ui.form_utils import preview_owned_file_params

    issues: list[DiagnosticIssue] = []
    if model.workflow_archetype != "multimodal_video":
        return issues

    owned = preview_owned_file_params(model)
    overlap_adv = owned & set(model.advanced_params)
    if overlap_adv:
        issues.append(
            DiagnosticIssue(
                "error",
                "duplicate_upload_advanced",
                "Preview-owned file params also listed in advanced_params: "
                f"{sorted(overlap_adv)}.",
            )
        )
    overlap_bal = owned & set(model.balanced_params)
    if overlap_bal:
        issues.append(
            DiagnosticIssue(
                "warning",
                "duplicate_upload_balanced",
                "Preview-owned file params also in balanced_params (must be "
                f"skipped in controls): {sorted(overlap_bal)}.",
            )
        )
    return issues


def probe_multimodal_frame_uploads() -> list[str]:
    """Verify preview-column frame uploads survive kwargs normalization."""
    from io import BytesIO

    from src.models_config import get_model_by_name
    from src.replicate_payload import build_replicate_input, generation_mode_for_payload
    from src.ui.form_utils import normalize_file_kwargs, set_upload_kwarg

    class _FakeUpload:
        def __init__(self, name: str) -> None:
            self.name = name
            self.type = "image/png"
            self.size = 100

        def getbuffer(self) -> BytesIO:
            return BytesIO(b"\x89PNG\r\n\x1a\n" + b"x" * 50)

    errors: list[str] = []
    scenarios: list[tuple[str, dict[str, Any], dict[str, _FakeUpload]]] = [
        (
            "kling-v3-omni",
            {
                "prompt": "probe",
                "mode": "pro",
                "duration": 5,
                "aspect_ratio": "16:9",
            },
            {
                "start_image": _FakeUpload("start.png"),
                "end_image": _FakeUpload("end.png"),
            },
        ),
        (
            "kling-o1",
            {
                "prompt": "probe",
                "mode": "pro",
                "duration": 5,
                "aspect_ratio": "16:9",
            },
            {"start_image": _FakeUpload("start.png")},
        ),
        (
            "seedance-2.0-fast",
            {
                "prompt": "probe",
                "duration": 5,
                "resolution": "720p",
                "aspect_ratio": "16:9",
            },
            {
                "image": _FakeUpload("start.png"),
                "last_frame_image": _FakeUpload("end.png"),
            },
        ),
    ]

    for model_name, base_kwargs, uploads in scenarios:
        model = get_model_by_name(model_name)
        kwargs = dict(base_kwargs)
        for param, upload in uploads.items():
            set_upload_kwarg(kwargs, param, upload)

        normalized = normalize_file_kwargs(model, kwargs)
        payload = build_replicate_input(model_name, **normalized)
        mode = generation_mode_for_payload(model, payload)
        if model_name.startswith("kling"):
            if "start_image" not in payload:
                errors.append(f"{model_name}: start_image missing from payload")
        else:
            if "image" not in payload:
                errors.append(f"{model_name}: image missing from payload")
        if mode == "text_to_video":
            errors.append(f"{model_name}: expected image_to_video, got {mode}")

    return errors


def compare_model_config(
    model: ModelConfig,
    remote: dict[str, Any] | None = None,
) -> ModelDiagnosticReport:
    """Compare local ModelConfig constraints against optional remote schema."""
    report = ModelDiagnosticReport(
        model_name=model.name, replicate_id=model.replicate_id
    )

    if model.provider != "replicate":
        report.issues.append(
            DiagnosticIssue(
                "info",
                "non_replicate",
                f"Skipping remote schema check for provider {model.provider!r}.",
            )
        )
        return report

    if remote is None:
        report.issues.append(
            DiagnosticIssue(
                "info",
                "remote_skipped",
                "Remote schema not fetched (missing REPLICATE_API_TOKEN "
                "or replicate package).",
            )
        )
    else:
        report.remote_fetched = True
        props = remote.get("properties", {})
        report.remote_properties = sorted(props.keys())
        report.remote_required = list(remote.get("required", []))

        if model.requires_text and "prompt" not in report.remote_required:
            if "prompt" in props:
                report.issues.append(
                    DiagnosticIssue(
                        "warning",
                        "required_prompt",
                        "Model marked requires_text but Replicate schema does not list "
                        "prompt as required.",
                    )
                )
        if model.requires_image and "image" not in report.remote_required:
            if "image" in props:
                report.issues.append(
                    DiagnosticIssue(
                        "warning",
                        "required_image",
                        "Model marked requires_image but Replicate schema "
                        "does not list image as required.",
                    )
                )

        for pname, constraints in model.param_constraints.items():
            if pname not in props:
                if pname in _configured_param_names(model):
                    report.issues.append(
                        DiagnosticIssue(
                            "warning",
                            "unknown_param",
                            f"Parameter {pname!r} not in remote Input schema.",
                        )
                    )
                continue

            prop = props[pname]
            remote_enum = _resolve_enum(prop)
            local_enum = get_options_for_param(model, pname)
            if local_enum is not None and remote_enum is not None:
                local_set = {str(v) for v in local_enum}
                remote_set = {str(v) for v in remote_enum}
                if local_set != remote_set:
                    report.issues.append(
                        DiagnosticIssue(
                            "error",
                            "enum_mismatch",
                            f"{pname}: local enum {sorted(local_enum)} != "
                            f"remote {sorted(remote_enum)}.",
                        )
                    )

            rmin, rmax = _resolve_min_max(prop)
            lmin, lmax = get_range_for_param(model, pname)
            if lmin is not None and rmin is not None and lmin != rmin:
                report.issues.append(
                    DiagnosticIssue(
                        "error",
                        "min_mismatch",
                        f"{pname}: local min {lmin} != remote min {rmin}.",
                    )
                )
            if lmax is not None and rmax is not None and lmax != rmax:
                report.issues.append(
                    DiagnosticIssue(
                        "error",
                        "max_mismatch",
                        f"{pname}: local max {lmax} != remote max {rmax}.",
                    )
                )

            str_max = constraints.get("max")
            remote_max_len = prop.get("maxLength")
            if (
                str_max is not None
                and remote_max_len is not None
                and str_max != remote_max_len
            ):
                report.issues.append(
                    DiagnosticIssue(
                        "warning",
                        "max_length_mismatch",
                        f"{pname}: local max chars {str_max} != remote maxLength "
                        f"{remote_max_len}.",
                    )
                )

        ui_params = _configured_param_names(model)
        if model.supports_text:
            ui_params.add("prompt")
        if model.supports_image:
            media_file_params = set(getattr(model, "file_input_params", {}))
            if "image" in media_file_params or not any(
                pname.endswith("image") or pname == "images"
                for pname in media_file_params
            ):
                ui_params.add("image")
        for pname in sorted(ui_params):
            if pname in props or pname in {
                "reference_images",
                "reference_videos",
                "reference_audios",
            }:
                continue
            if pname in model.defaults and model.defaults.get(pname) in ([], None):
                continue
            report.issues.append(
                DiagnosticIssue(
                    "warning",
                    "ui_param_missing_remote",
                    f"UI exposes {pname!r} but it is absent from remote Input schema.",
                )
            )

    if model.provider_endpoint == "versionless":
        report.issues.append(
            DiagnosticIssue(
                "info",
                "endpoint_mode",
                "Uses versionless Replicate API (predictions.create model=...).",
            )
        )
    else:
        report.issues.append(
            DiagnosticIssue(
                "info",
                "endpoint_mode",
                "Uses versioned Replicate API (predictions.create version=...).",
            )
        )

    if not model.metadata_verified_date:
        report.issues.append(
            DiagnosticIssue(
                "warning",
                "metadata_date",
                "metadata_verified_date is empty.",
            )
        )

    report.issues.extend(audit_capability_ui_config(model))

    return report


def run_all_diagnostics(fetch_remote: bool = True) -> list[ModelDiagnosticReport]:
    """Run diagnostics for every configured model."""
    reports: list[ModelDiagnosticReport] = []
    for model in ALL_MODELS:
        remote = None
        if fetch_remote:
            remote = fetch_remote_input_schema(model.replicate_id)
        reports.append(compare_model_config(model, remote))
    return reports


def format_report_text(report: ModelDiagnosticReport) -> str:
    """Plain-text summary for CLI output."""
    lines = [
        f"=== {report.model_name} ({report.replicate_id}) ===",
        f"remote_fetched: {report.remote_fetched}",
    ]
    if report.remote_required:
        lines.append(f"remote required: {report.remote_required}")
    for issue in report.issues:
        lines.append(f"  [{issue.severity}] {issue.code}: {issue.message}")
    return "\n".join(lines)


def validate_presets() -> list[str]:
    """Return local preset values that violate model constraints."""
    errors: list[str] = []
    for model in ALL_MODELS:
        for preset_name, values in (model.presets or {}).items():
            for pname, value in values.items():
                enum_vals = get_options_for_param(model, pname)
                if enum_vals is not None and value not in enum_vals:
                    errors.append(
                        f"{model.name} preset {preset_name!r}: {pname}={value!r} "
                        f"is not in {enum_vals!r}"
                    )
                min_val, max_val = get_range_for_param(model, pname)
                if isinstance(value, (int, float)) and not isinstance(value, bool):
                    if min_val is not None and value < min_val:
                        errors.append(
                            f"{model.name} preset {preset_name!r}: {pname}={value!r} "
                            f"is below minimum {min_val!r}"
                        )
                    if max_val is not None and value > max_val:
                        errors.append(
                            f"{model.name} preset {preset_name!r}: {pname}={value!r} "
                            f"is above maximum {max_val!r}"
                        )
    return errors


def all_reports_ok(reports: list[ModelDiagnosticReport]) -> bool:
    """Return True when no report has error-severity issues."""
    return all(r.ok for r in reports)
