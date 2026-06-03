# v0.3.1 Implementation — 3D Endpoint Compatibility Patch

> **Project note:** This patch fixes a real Replicate API compatibility problem without running paid predictions.

**Goal:** Fix Hunyuan3D 2.0 / TRELLIS 2 404 errors caused by using Replicate's versionless model prediction endpoint for models that require versioned prediction creation.

**Architecture:** Keep user-facing model IDs as owner/name slugs in `ModelConfig`, but have the 3D generation wrapper resolve `model.latest_version.id` at runtime and call `replicate.predictions.create(version=..., input=...)`. Cache the version lookup per process to avoid repeated metadata calls.

**Verification approach:** Use non-paid local probes and Replicate model metadata lookups only. Do not create live predictions without explicit user authorization.

---

## Triggering issue

Hunyuan3D 2.0 generation failed with:

```text
Unexpected error: ReplicateError Details: status: 404 detail: The requested resource could not be found
```

Investigation showed:

- `https://replicate.com/tencent/hunyuan3d-2` exists.
- Replicate metadata reports `usesVersionlessApi: false` for `tencent/hunyuan3d-2`.
- Calling `replicate.predictions.create(model="tencent/hunyuan3d-2", input=...)` uses `/v1/models/tencent/hunyuan3d-2/predictions`, which can 404 for this model.
- The model works through the versioned prediction API using its latest version ID.

---

## Implemented changes

### Code

- `src/threed_gen.py`
  - Added `_latest_version_id(model_id)` with `@lru_cache(maxsize=16)`.
  - Changed 3D prediction creation from `model=model_id` to `version=version_id`.
  - Kept existing polling/output/history behavior.

- `src/utils.py`
  - Added `friendly_error_message()` for common Replicate/API failures:
    - 401 / unauthorized
    - 404 / not found
    - 422 / validation
    - timeout/network/connection

- `app.py`
  - Uses `friendly_error_message()` for failed result messages and unexpected generation exceptions.

### Documentation/versioning

- `pyproject.toml` version bumped to `0.3.1`.
- `uv.lock` package version updated to `0.3.1`.
- `README.md` current version/status updated.
- `CHANGELOG.md` added v0.3.1 entry and marked v0.3.0 superseded.
- `ROADMAP.md` marked v0.3.1 as the current patch release.
- `DECISIONS.md` added the Replicate prediction endpoint-mode decision.

---

## Non-paid verification

### RED probe before fix

Confirmed the old 3D path called:

```python
{"model": "tencent/hunyuan3d-2", "input": {...}}
```

### GREEN probe after fix

Confirmed the 3D path calls:

```python
{"version": "version-123", "input": {...}}
```

with a fake Replicate model/prediction client.

### Metadata verification

Verified latest version IDs through Replicate's model API without creating predictions:

- `tencent/hunyuan3d-2`
  - `b1b9449a1277e10402781c5d41eb30c0a0683504fb23fab591ca9dfc2aabe1cb`
- `fishwowater/trellis2`
  - `52e1ad6852599ea10ce8e257635a3c11485cba51c181ea5173e34d9b2955b226`

### Local checks

Run before marking complete:

```bash
python -m compileall -q app.py src
uv run ruff check .
uv lock --check
```

No paid Replicate prediction is required for v0.3.1 completion.

---

## Known limitations

- No live paid image-to-3D smoke generation was run for this patch.
- Output URLs are still temporary and expire after about 1 hour.
- Durable local output storage remains planned for v0.4.0.
- Endpoint-mode metadata is still implicit in the generation wrapper; richer model capability metadata is planned before or shortly after v1.0.
