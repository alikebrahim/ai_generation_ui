# AGENTS.md — AI Generation UI Project Guidelines

This document defines conventions, defaults, and constraints for this project. Follow these when implementing or modifying code.

## Project Scope

**IN SCOPE:**
- Video generation: Text-to-Video (T2V), Image-to-Video (I2V)
- 3D generation: Image-to-3D (I23D); Text-to-3D (T23D) is future scope unless a reliable Replicate text-capable model is added
- Replicate API integration only
- Streamlit-based web interface
- Cost tracking and generation history

**OUT OF SCOPE:**
- Image generation (handled by ComfyUI workflows separately)
- Audio generation
- Video-to-video transformations (future consideration)
- Local model inference (all generation via Replicate API)

## Tooling & Dependencies

### Package Management
- **uv** for dependency management and virtual environments
- `pyproject.toml` for project configuration
- No `requirements.txt` — uv uses pyproject.toml directly

### Core Dependencies (Latest Stable Versions)
```toml
streamlit = ">=1.58.0"       # Web UI framework
replicate = ">=1.0.7"        # Replicate API client
python-dotenv = ">=1.2.2"    # Environment variable management
pillow = ">=10.0.0"          # Image processing
requests = ">=2.31.0"        # HTTP client for downloads
```

### Development Dependencies
```toml
ruff = ">=0.4.0"             # Fast Python linter
black = ">=24.0.0"           # Code formatter
```

### Environment Variables
- Use `.env` file (gitignored) for secrets
- `.env.example` for template
- Load via `python-dotenv` at app startup
- Never hardcode API tokens in code

## Architecture Decisions

### API Layer
- Use `replicate` Python package (official client)
- One module per generation type: `src/video_gen.py`, `src/threed_gen.py`
- Cost tracking module: `src/cost_tracker.py`
- Each model gets its own function with typed parameters
- API calls are async-friendly but start synchronous for simplicity

### Cost Tracking & History
- Replicate provides `metrics` field in prediction responses with:
  - `predict_time`: Duration in seconds
  - `total_time`: Total time including queue
  - Hardware info (when available)
- Store generation metadata in SQLite database: `data/history.db`
- Track per-generation:
  - Model name, timestamp, prompt
  - Input parameters (resolution, duration, etc.)
  - Generation time, cost estimate
  - Output file path
- Display stats in "History" tab:
  - Total spend per model
  - Total spend overall
  - Generation count per model
  - Recent generations gallery

### File Storage
- Outputs are NOT stored locally on the server
- Replicate provides ephemeral URLs for preview (expire after ~1 hour)
- User downloads explicitly from the displayed Replicate/local output link
- Only metadata is persisted: prompt, params, cost, timestamp, replicate_url
- No `outputs/` directory needed — removed from project structure

### Streamlit App Structure
- Single-page app with tabs: Video | 3D | History
- **Video Tab**:
  - Model selector dropdown
  - Input form (text prompt, image upload if applicable)
  - Parameter sliders/toggles split into two categories:
    - **Balanced** (always visible): prompt, duration/resolution, seed, aspect ratio, negative prompt
    - **Advanced** (in collapsible expander): guidance scale, inference steps, scheduler type, motion strength
  - Generate button
  - Output display area (video player)
  - Download button for output file
  - Cost estimate display
- **3D Tab**: Same structure with 3D viewer instead of video player; current models are image-to-3D
- **History Tab**:
  - Summary stats (total spend, generations by model)
  - Filterable table of past generations
  - Links to re-open outputs
- Use `st.session_state` to persist form inputs during generation

### UI Components
- **Video display**: `st.video()` — native Streamlit, battle-tested
- **3D display**: Google's `<model-viewer>` via `st.components.v1.html()`
  - Inject HTML/JS with model URL as parameter
  - Supports rotation, zoom, lighting
- **Image upload**: `st.file_uploader()` with preview
- **Progress**: `st.progress()` for polling Replicate API status
- **Error handling**: `st.error()` with user-friendly messages
- **Cost display**: Show estimated cost before generation, actual after

### Code Style
- Python 3.11+
- Type hints on all function signatures
- Docstrings on public functions
- Black formatter, 88 char line length
- Ruff for linting (configured in pyproject.toml)

### Configuration
- API token via `.env` file (loaded with python-dotenv)
- No hardcoded model versions — use `latest` alias or fetch version list
- Model configurations in `src/models_config.py` (dataclasses mapping model names to their Replicate identifiers, capability flags, parameter groups, and defaults)

## Naming Conventions

- **Files**: `snake_case.py`
- **Functions**: `snake_case`
- **Constants**: `UPPER_SNAKE_CASE`
- **Streamlit pages**: Single file `app.py` (not multi-page structure)

## Error Handling Strategy

1. **API errors**: Catch `replicate.exceptions.ReplicateError`, show friendly message
2. **Network errors**: Retry up to 3 times with exponential backoff for transient failures
3. **Invalid inputs**: Validate before API call, show `st.error()` immediately
4. **File errors**: Ensure output directory exists, catch write permission errors
5. **Cost calculation**: If metrics missing, show "Cost unknown" rather than crashing

## Testing Approach

- Manual testing during development (no formal test suite initially)
- Test each model end-to-end: prompt → generate → display → download
- Verify error paths: invalid token, network timeout, invalid input
- Test cost tracking: verify costs are recorded and displayed correctly

## Performance Guidelines

- **Video generation**: 30 seconds to 5 minutes typical
  - Poll Replicate API every 5 seconds
  - Show progress bar with estimated time
- **3D generation**: 1 to 10 minutes typical
  - Poll every 10 seconds
  - Show spinner with status message
- **File downloads**: Use link buttons for Replicate delivery URLs; future local storage may use `st.download_button()` or file-serving links
- **History queries**: Index SQLite database on model_name and timestamp for fast filtering

## Security

- Never log or display the Replicate API token
- `.env` file must be in `.gitignore`
- Validate file uploads (size, type) before processing
- Sanitize user prompts (basic length limit, no code injection)

## Dependencies Installation

```bash
# Create venv and install deps
uv venv
uv pip install -e .

# For development
uv pip install -e ".[dev]"
```

## Git Workflow

- Commit messages: `feat:`, `fix:`, `docs:`, `refactor:`, `chore:`
- One feature per branch
- No `main` branch protection initially (solo dev)
- `.gitignore` must include: `.env`, `.venv/`, `__pycache__/`, `*.pyc`, `data/`

## Future Extensibility

Design with these future additions in mind (but don't implement now):
- Generation history/gallery view (PLANNED for initial release)
- Side-by-side model comparison
- Batch generation (multiple prompts)
- ComfyUI integration for image preprocessing
- Local model support (Hunyuan3D-2 on local GPU)
- Export history to CSV/JSON

## Deployment

- Local development only for now
- Run with: `streamlit run app.py`
- Default port: 8501
- No Docker initially (keep it simple)

## Database Schema (for history tracking)

```sql
CREATE TABLE generations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name TEXT NOT NULL,
    model_type TEXT NOT NULL,  -- 'video' or '3d'
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    prompt TEXT,
    input_image_path TEXT,  -- NULL for text-only
    parameters_json TEXT,   -- JSON string of generation params
    replicate_url TEXT NOT NULL,
    predict_time_seconds REAL,
    total_time_seconds REAL,
    estimated_cost_usd REAL,
    status TEXT  -- 'success', 'failed', 'cancelled'
);

CREATE INDEX idx_model_name ON generations(model_name);
CREATE INDEX idx_timestamp ON generations(timestamp);
```
