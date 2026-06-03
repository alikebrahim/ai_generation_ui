# Implementation Plan

This document is a historical pre-implementation blueprint for the first build.
It is retained for context, not as current guidance.

For current development, use:
- `README.md` for project status and quick start
- `CHANGELOG.md` for standard version history
- `ROADMAP.md` for the versioned plan from v0.2.0 toward v1.0.0
- `ITER_1_IMPLEMENTATION.md` for the current as-built reference

Known historical differences in this file:
- It uses `lib/`; the implemented source layout is `src/`.
- It references older TRELLIS assumptions; the current implemented model ID is
  `fishwowater/trellis2`.
- It shows blocking `prediction.wait()` examples; the current implementation polls
  Replicate predictions and updates the UI with status.

---

## Overview

The project is divided into 5 phases:
1. **Phase 0: Project Bootstrap** - Set up project structure and dependencies
2. **Phase 1: Core Infrastructure** - Build foundational modules (config, pricing, cost tracking)
3. **Phase 2: Video Generation** - Implement video model integrations
4. **Phase 3: 3D Generation** - Implement 3D model integrations
5. **Phase 4: Streamlit UI** - Build the web interface
6. **Phase 5: Polish** - Error handling, testing, refinement

---

## Phase 0: Project Bootstrap

### Step 1: Verify Project Structure

**Action**: Check that all required directories exist

```bash
cd /home/tima/ai_generation_ui
mkdir -p lib data assets
```

**Verification**: `ls -la` should show all directories

---

### Step 2: Create .gitignore

**Action**: Create `.gitignore` with standard exclusions

```bash
cat > .gitignore << 'EOF'
# Environment
.env
.venv/

# Python
__pycache__/
*.pyc
*.pyo
*.pyd
.Python

# Database
data/

# IDE
.vscode/
.idea/
*.swp
*.swo

# OS
.DS_Store
Thumbs.db
EOF
```

**Verification**: `cat .gitignore` shows the file

---

### Step 3: Set Up Python Environment

**Action**: Create virtual environment and install dependencies

```bash
uv venv
uv pip install -e .
```

**Verification**: `uv pip list` shows streamlit, replicate, python-dotenv

---

### Step 4: Configure API Token

**Action**: Create `.env` file from template

```bash
cp .env.example .env
nano .env
```

**Edit**: Add your Replicate API token (from https://replicate.com/account/api-tokens)

```
REPLICATE_API_TOKEN=r8_***
```

**Verification**: `cat .env` shows the token (not committed to git)

---

### Step 5: Test Environment

**Action**: Verify imports work

```bash
source .venv/bin/activate
python -c "import streamlit; import replicate; print('OK')"
```

**Expected Output**: `OK`

---

## Phase 1: Core Infrastructure

### Step 6: Create lib/config.py

**Purpose**: Centralize configuration, paths, and environment loading

**Implementation**:
```python
"""Configuration and environment setup."""
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# API configuration
REPLICATE_API_TOKEN = os.getenv("REPLICATE_API_TOKEN")
if not REPLICATE_API_TOKEN:
    raise ValueError("REPLICATE_API_TOKEN not found in .env")

# Project paths
PROJECT_ROOT = Path(__file__).parent.parent
DATA_DIR = PROJECT_ROOT / "data"
ASSETS_DIR = PROJECT_ROOT / "assets"

# Ensure directories exist
DATA_DIR.mkdir(parents=True, exist_ok=True)

# Database
HISTORY_DB = DATA_DIR / "history.db"

# Constants
POLL_INTERVAL_VIDEO = 5  # seconds
POLL_INTERVAL_3D = 10  # seconds
MAX_RETRIES = 3
```

**Verification**: `python -c "from lib.config import REPLICATE_API_TOKEN; print('Token loaded')"`

---

### Step 7: Create lib/pricing.py

**Purpose**: Static pricing table for cost calculation

**Implementation**:
```python
"""Pricing table for Replicate hardware and models."""

# Hardware pricing (USD per second)
# Source: https://replicate.com/pricing (as of 2024)
HARDWARE_PRICING = {
    "t4": 0.000275,
    "a40": 0.000725,
    "a40-large": 0.000725,
    "a100-40gb": 0.00115,
    "a100-80gb": 0.00140,
}

# Model to hardware mapping
# TODO: Fetch from replicate.models.get() on first run
MODEL_HARDWARE = {
    "wan-video/wan-2.7-t2v": "a40",
    "wan-video/wan-2.5-i2v-fast": "a40",
    "bytedance/seedance-2.0": "a100-40gb",
    "tencent/hunyuan3d-2": "a100-40gb",
    "microsoft/trellis-2": "a40",
}

def get_price_per_second(model_name: str) -> float:
    """Get price per second for a model."""
    hardware = MODEL_HARDWARE.get(model_name, "a40")
    return HARDWARE_PRICING.get(hardware, 0.000725)  # Default to a40

def calculate_cost(model_name: str, predict_time: float) -> float:
    """Calculate cost for a prediction."""
    price_per_sec = get_price_per_second(model_name)
    return predict_time * price_per_sec
```

**Verification**: `python -c "from lib.pricing import calculate_cost; print(calculate_cost('wan-video/wan-2.7-t2v', 60.0))"`

---

### Step 8: Create lib/models_config.py

**Purpose**: Define model identifiers and parameter schemas

**Implementation**:
```python
"""Model configurations and parameter schemas."""
from dataclasses import dataclass
from typing import Literal

@dataclass
class ModelConfig:
    """Configuration for a Replicate model."""
    name: str
    display_name: str
    model_type: Literal["video", "3d"]
    replicate_id: str
    supports_text: bool
    supports_image: bool
    balanced_params: list[str]
    advanced_params: list[str]

# Video models
WAN_2_7_T2V = ModelConfig(
    name="wan-2.7-t2v",
    display_name="Wan 2.7 T2V",
    model_type="video",
    replicate_id="wan-video/wan-2.7-t2v",
    supports_text=True,
    supports_image=False,
    balanced_params=["prompt", "duration", "aspect_ratio", "seed"],
    advanced_params=["guidance_scale", "num_inference_steps", "negative_prompt"],
)

WAN_2_5_I2V = ModelConfig(
    name="wan-2.5-i2v-fast",
    display_name="Wan 2.5 I2V Fast",
    model_type="video",
    replicate_id="wan-video/wan-2.5-i2v-fast",
    supports_text=True,
    supports_image=True,
    balanced_params=["prompt", "image", "duration", "aspect_ratio", "seed"],
    advanced_params=["guidance_scale", "num_inference_steps", "negative_prompt"],
)

SEEDANCE_2_0 = ModelConfig(
    name="seedance-2.0",
    display_name="Seedance 2.0",
    model_type="video",
    replicate_id="bytedance/seedance-2.0",
    supports_text=True,
    supports_image=True,
    balanced_params=["prompt", "image", "duration", "aspect_ratio", "seed"],
    advanced_params=["guidance_scale", "num_inference_steps", "negative_prompt", "motion_strength"],
)

# 3D models
HUNYUAN3D_2 = ModelConfig(
    name="hunyuan3d-2",
    display_name="Hunyuan3D 2.0",
    model_type="3d",
    replicate_id="tencent/hunyuan3d-2",
    supports_text=True,
    supports_image=True,
    balanced_params=["prompt", "image", "seed"],
    advanced_params=["guidance_scale", "num_inference_steps", "negative_prompt"],
)

TRELLIS_2 = ModelConfig(
    name="trellis-2",
    display_name="TRELLIS 2",
    model_type="3d",
    replicate_id="microsoft/trellis-2",
    supports_text=False,
    supports_image=True,
    balanced_params=["image", "seed"],
    advanced_params=["guidance_scale", "num_inference_steps"],
)

# Collections
VIDEO_MODELS = [WAN_2_7_T2V, WAN_2_5_I2V, SEEDANCE_2_0]
THREED_MODELS = [HUNYUAN3D_2, TRELLIS_2]
ALL_MODELS = VIDEO_MODELS + THREED_MODELS

def get_model_by_name(name: str) -> ModelConfig:
    """Get model config by name."""
    for model in ALL_MODELS:
        if model.name == name:
            return model
    raise ValueError(f"Model not found: {name}")
```

**Verification**: `python -c "from lib.models_config import VIDEO_MODELS; print([m.name for m in VIDEO_MODELS])"`

---

### Step 9: Create lib/cost_tracker.py

**Purpose**: SQLite database for tracking generation history and costs

**Implementation**:
```python
"""Cost tracking and generation history."""
import sqlite3
import json
from datetime import datetime
from pathlib import Path
from .config import HISTORY_DB

def init_db():
    """Initialize the database schema."""
    conn = sqlite3.connect(HISTORY_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS generations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            model_name TEXT NOT NULL,
            model_type TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            prompt TEXT,
            input_image_path TEXT,
            parameters_json TEXT,
            replicate_url TEXT NOT NULL,
            predict_time_seconds REAL,
            total_time_seconds REAL,
            estimated_cost_usd REAL,
            status TEXT DEFAULT 'success'
        )
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_model_name 
        ON generations(model_name)
    """)
    
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_timestamp 
        ON generations(timestamp)
    """)
    
    conn.commit()
    conn.close()

def record_generation(
    model_name: str,
    model_type: str,
    prompt: str,
    parameters: dict,
    replicate_url: str,
    predict_time: float,
    total_time: float,
    estimated_cost: float,
    input_image_path: str = None,
    status: str = "success"
) -> int:
    """Record a generation in the database."""
    conn = sqlite3.connect(HISTORY_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        INSERT INTO generations (
            model_name, model_type, prompt, input_image_path,
            parameters_json, replicate_url, predict_time_seconds,
            total_time_seconds, estimated_cost_usd, status
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        model_name, model_type, prompt, input_image_path,
        json.dumps(parameters), replicate_url, predict_time,
        total_time, estimated_cost, status
    ))
    
    generation_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return generation_id

def get_all_generations(limit: int = 100):
    """Get all generations, most recent first."""
    conn = sqlite3.connect(HISTORY_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT * FROM generations 
        ORDER BY timestamp DESC 
        LIMIT ?
    """, (limit,))
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows

def get_stats_by_model():
    """Get statistics grouped by model."""
    conn = sqlite3.connect(HISTORY_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            model_name,
            COUNT(*) as count,
            SUM(estimated_cost_usd) as total_cost,
            AVG(predict_time_seconds) as avg_time
        FROM generations
        WHERE status = 'success'
        GROUP BY model_name
    """)
    
    rows = cursor.fetchall()
    conn.close()
    
    return rows

def get_total_stats():
    """Get overall statistics."""
    conn = sqlite3.connect(HISTORY_DB)
    cursor = conn.cursor()
    
    cursor.execute("""
        SELECT 
            COUNT(*) as total_count,
            SUM(estimated_cost_usd) as total_cost,
            AVG(predict_time_seconds) as avg_time
        FROM generations
        WHERE status = 'success'
    """)
    
    row = cursor.fetchone()
    conn.close()
    
    return row
```

**Verification**: 
```bash
python -c "from lib.cost_tracker import init_db; init_db(); print('DB initialized')"
ls data/history.db
```

---

### Step 10: Create lib/utils.py

**Purpose**: Utility functions for formatting and display

**Implementation**:
```python
"""Utility functions."""
from datetime import datetime

def format_cost(cost: float) -> str:
    """Format cost as USD string."""
    return f"${cost:.2f}"

def format_duration(seconds: float) -> str:
    """Format duration in human-readable form."""
    if seconds < 60:
        return f"{seconds:.1f}s"
    elif seconds < 3600:
        minutes = seconds / 60
        return f"{minutes:.1f}m"
    else:
        hours = seconds / 3600
        return f"{hours:.1f}h"
```

**Verification**: `python -c "from lib.utils import format_cost; print(format_cost(0.42))"`

---

## Phase 2: Video Generation

### Step 11: Create lib/video_gen.py

**Purpose**: Implement video generation functions for all 3 video models

**Implementation** (partial - one model as example):
```python
"""Video generation using Replicate API."""
import replicate
from .models_config import WAN_2_7_T2V
from .pricing import calculate_cost
from .cost_tracker import record_generation

def generate_wan_2_7_t2v(
    prompt: str,
    duration: float = 5.0,
    aspect_ratio: str = "16:9",
    seed: int = None,
    guidance_scale: float = 7.5,
    num_inference_steps: int = 50,
    negative_prompt: str = None,
) -> dict:
    """Generate video using Wan 2.7 T2V. Returns dict with url + metadata."""
    
    # Prepare input parameters
    input_params = {
        "prompt": prompt,
        "duration": duration,
        "aspect_ratio": aspect_ratio,
        "guidance_scale": guidance_scale,
        "num_inference_steps": num_inference_steps,
    }
    
    if seed is not None:
        input_params["seed"] = seed
    if negative_prompt:
        input_params["negative_prompt"] = negative_prompt
    
    # Create prediction
    prediction = replicate.predictions.create(
        model=WAN_2_7_T2V.replicate_id,
        input=input_params
    )
    
    # Poll for completion
    prediction.wait()
    
    # Check status
    if prediction.status != "succeeded":
        return {
            "success": False,
            "error": f"Prediction failed: {prediction.error}"
        }
    
    # Get output URL (no local download)
    output_url = prediction.output
    
    # Calculate cost
    predict_time = prediction.metrics.get("predict_time", 0)
    total_time = prediction.metrics.get("total_time", 0)
    estimated_cost = calculate_cost(WAN_2_7_T2V.replicate_id, predict_time)
    
    # Record in database
    record_generation(
        model_name=WAN_2_7_T2V.name,
        model_type="video",
        prompt=prompt,
        parameters=input_params,
        replicate_url=output_url,
        predict_time=predict_time,
        total_time=total_time,
        estimated_cost=estimated_cost,
        status="success"
    )
    
    return {
        "success": True,
        "url": output_url,
        "predict_time": predict_time,
        "total_time": total_time,
        "estimated_cost": estimated_cost
    }

# TODO: Implement generate_wan_2_5_i2v()
# TODO: Implement generate_seedance_2_0()
```

**Verification**: Test with a simple prompt (will cost ~$0.20):
```python
from lib.video_gen import generate_wan_2_7_t2v
result = generate_wan_2_7_t2v(prompt="A cat playing piano", duration=3.0)
print(result)
```

**Note**: Complete all 3 video model functions following the same pattern.

---

## Phase 3: 3D Generation

### Step 12: Create lib/threed_gen.py

**Purpose**: Implement 3D generation functions for both 3D models

**Implementation** (similar pattern to video_gen.py):
```python
"""3D generation using Replicate API."""
import replicate
from .models_config import HUNYUAN3D_2, TRELLIS_2
from .pricing import calculate_cost
from .cost_tracker import record_generation

def generate_hunyuan3d_2(
    prompt: str = None,
    image: Path = None,
    seed: int = None,
    guidance_scale: float = 7.5,
    num_inference_steps: int = 50,
    negative_prompt: str = None,
) -> dict:
    """Generate 3D model using Hunyuan3D 2.0. Returns dict with url + metadata."""
    
    # Prepare input parameters
    input_params = {
        "guidance_scale": guidance_scale,
        "num_inference_steps": num_inference_steps,
    }
    
    if prompt:
        input_params["prompt"] = prompt
    if image:
        input_params["image"] = open(image, "rb")
    if seed is not None:
        input_params["seed"] = seed
    if negative_prompt:
        input_params["negative_prompt"] = negative_prompt
    
    # Create prediction
    prediction = replicate.predictions.create(
        model=HUNYUAN3D_2.replicate_id,
        input=input_params
    )
    
    # Poll for completion
    prediction.wait()
    
    # Check status
    if prediction.status != "succeeded":
        return {
            "success": False,
            "error": f"Prediction failed: {prediction.error}"
        }
    
    # Get output URL (no local download)
    output_url = prediction.output
    
    # Calculate cost
    predict_time = prediction.metrics.get("predict_time", 0)
    total_time = prediction.metrics.get("total_time", 0)
    estimated_cost = calculate_cost(HUNYUAN3D_2.replicate_id, predict_time)
    
    # Record in database
    record_generation(
        model_name=HUNYUAN3D_2.name,
        model_type="3d",
        prompt=prompt or "",
        parameters=input_params,
        replicate_url=output_url,
        predict_time=predict_time,
        total_time=total_time,
        estimated_cost=estimated_cost,
        input_image_path=str(image) if image else None,
        status="success"
    )
    
    return {
        "success": True,
        "url": output_url,
        "predict_time": predict_time,
        "total_time": total_time,
        "estimated_cost": estimated_cost
    }

# TODO: Implement generate_trellis_2()
```

**Verification**: Test with a simple prompt (will cost ~$0.50-1.00):
```python
from lib.threed_gen import generate_hunyuan3d_2
result = generate_hunyuan3d_2(prompt="A cute robot")
print(result)
```

**Note**: Complete both 3D model functions. TRELLIS 2 requires image input only.

---

## Phase 4: Streamlit UI

### Step 13: Create app.py - Basic Structure

**Purpose**: Main Streamlit application with tab layout

**Implementation** (basic structure):
```python
"""Main Streamlit application."""
import streamlit as st
from lib.cost_tracker import init_db, get_total_stats, get_stats_by_model
from lib.models_config import VIDEO_MODELS, THREED_MODELS

# Page configuration
st.set_page_config(
    page_title="AI Generation UI",
    page_icon="🎬",
    layout="wide"
)

# Initialize database on first run
init_db()

# Title
st.title("AI Generation Studio")
st.markdown("Generate videos and 3D models using Replicate API")

# Create tabs
tab_video, tab_3d, tab_history = st.tabs(["Video Generation", "3D Generation", "History"])

# Video tab
with tab_video:
    st.header("Video Generation")
    st.markdown("Generate videos from text or images")
    
    # Model selector
    model_options = {m.display_name: m.name for m in VIDEO_MODELS}
    selected_model = st.selectbox(
        "Select Model",
        options=list(model_options.keys()),
        key="video_model_selector"
    )
    
    # TODO: Add input form, parameters, generate button, output display

# 3D tab
with tab_3d:
    st.header("3D Generation")
    st.markdown("Generate 3D models from text or images")
    
    # Model selector
    model_options = {m.display_name: m.name for m in THREED_MODELS}
    selected_model = st.selectbox(
        "Select Model",
        options=list(model_options.keys()),
        key="3d_model_selector"
    )
    
    # TODO: Add input form, parameters, generate button, output display

# History tab
with tab_history:
    st.header("Generation History")
    
    # TODO: Display statistics and generation history table
```

**Verification**: Run the app:
```bash
streamlit run app.py
```
Open http://localhost:8501 - should see 3 tabs

---

### Step 14: Implement Video Tab UI

**Purpose**: Complete video generation interface with parameter forms and output display

**Implementation** (add to video tab):
```python
# Get selected model config
model_name = model_options[selected_model]
model_config = get_model_by_name(model_name)

# Input form
st.subheader("Input")
col1, col2 = st.columns([2, 1])

with col1:
    prompt = st.text_area(
        "Prompt",
        placeholder="Describe the video you want to generate...",
        height=100
    )

with col2:
    if model_config.supports_image:
        uploaded_image = st.file_uploader(
            "Upload Image (optional)",
            type=["png", "jpg", "jpeg"]
        )

# Balanced parameters (always visible)
st.subheader("Parameters")
col1, col2 = st.columns(2)

with col1:
    duration = st.slider("Duration (seconds)", 1.0, 10.0, 5.0, 0.5)
    aspect_ratio = st.selectbox("Aspect Ratio", ["16:9", "9:16", "1:1", "4:3"], index=0)

with col2:
    seed = st.number_input("Seed (optional, -1 for random)", value=-1, step=1)
    if seed == -1:
        seed = None

# Advanced parameters (in expander)
with st.expander("Advanced Parameters"):
    col1, col2 = st.columns(2)
    with col1:
        guidance_scale = st.slider("Guidance Scale", 1.0, 20.0, 7.5, 0.5)
    with col2:
        num_inference_steps = st.slider("Inference Steps", 10, 100, 50, 5)
    negative_prompt = st.text_area("Negative Prompt (optional)", height=80)

# Generate button
if st.button("Generate Video", type="primary"):
    if not prompt and not model_config.supports_image:
        st.error("Please enter a prompt")
    else:
        with st.spinner("Generating video..."):
            # TODO: Call appropriate generation function
            # result = generate_...(prompt, ...)
            
            # Display result
            if result["success"]:
                st.success(f"Video generated in {result['predict_time']:.1f}s")
                st.video(result["url"])
                
                col1, col2 = st.columns(2)
                with col1:
                    st.markdown(f"[Download Video]({result['url']})")
                with col2:
                    st.metric("Estimated Cost", f"${result['estimated_cost']:.2f}")
            else:
                st.error(f"Generation failed: {result['error']}")
```

**Verification**: Test video generation end-to-end

---

### Step 15: Implement 3D Tab UI

**Purpose**: Complete 3D generation interface with model-viewer display

**Implementation** (similar to video tab, but with 3D viewer):
```python
# Add to 3D tab after model selector
# ... (similar input form and parameters as video tab)

# Generate button
if st.button("Generate 3D Model", type="primary"):
    # ... (similar generation logic)
    
    if result["success"]:
        st.success(f"3D model generated in {result['predict_time']:.1f}s")
        
        # Display 3D model using model-viewer (uses Replicate URL directly)
        viewer_html = f"""
        <model-viewer 
            src="{result['url']}"
            alt="Generated 3D model"
            auto-rotate
            camera-controls
            style="width: 100%; height: 500px;">
        </model-viewer>
        <script type="module" src="https://ajax.googleapis.com/ajax/libs/model-viewer/3.5.0/model-viewer.min.js"></script>
        """
        st.components.v1.html(viewer_html, height=520)
        
        # Download button and cost display
        # ... (similar to video tab)
```

**Note**: model-viewer requires the file to be accessible via URL. You may need to serve the file via a local HTTP server or use base64 encoding. Alternative: use Streamlit's `st.file_uploader` in reverse or a custom component.

---

### Step 16: Implement History Tab

**Purpose**: Display generation statistics and history table

**Implementation**:
```python
# Add to history tab

# Summary statistics
st.subheader("Summary")
total_stats = get_total_stats()
if total_stats and total_stats[0] > 0:
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Total Generations", total_stats[0])
    with col2:
        st.metric("Total Cost", f"${total_stats[1]:.2f}")
    with col3:
        st.metric("Avg. Time", f"{total_stats[2]:.1f}s")
else:
    st.info("No generations yet. Start creating!")

# Per-model statistics
st.subheader("By Model")
model_stats = get_stats_by_model()
if model_stats:
    for row in model_stats:
        model_name, count, total_cost, avg_time = row
        with st.expander(f"{model_name} ({count} generations)"):
            st.metric("Total Cost", f"${total_cost:.2f}")
            st.metric("Avg. Time", f"{avg_time:.1f}s")

# Generation history table
st.subheader("Recent Generations")
generations = get_all_generations(limit=50)
if generations:
    import pandas as pd
    df = pd.DataFrame(generations, columns=[
        "ID", "Model", "Type", "Timestamp", "Prompt", "Input Image",
        "Parameters", "URL", "Predict Time", "Total Time",
        "Estimated Cost", "Status"
    ])
    
    # Display subset of columns
    display_df = df[["Timestamp", "Model", "Type", "Prompt", "Predict Time", "Estimated Cost", "Status"]]
    display_df["Predict Time"] = display_df["Predict Time"].apply(lambda x: f"{x:.1f}s")
    display_df["Estimated Cost"] = display_df["Estimated Cost"].apply(lambda x: f"${x:.2f}")
    
    st.dataframe(display_df, width="stretch")
else:
    st.info("No history available")
```

**Verification**: Generate a few videos/3D models, then check History tab

---

## Phase 5: Polish

### Step 17: Add Error Handling

**Purpose**: Robust error handling and user feedback

**Implementation**:
```python
# Add to lib/utils.py
def show_error_with_retry(error_message: str, retry_callback=None):
    """Display error with optional retry button."""
    st.error(f"Error: {error_message}")
    if retry_callback and st.button("Retry"):
        retry_callback()

# In app.py, wrap generation calls in try-except
try:
    result = generate_wan_2_7_t2v(prompt, ...)
    if result["success"]:
        st.toast("Generation complete! 🎉")
    else:
        st.error(result["error"])
except Exception as e:
    st.error(f"Unexpected error: {str(e)}")
```

---

### Step 18: Test End-to-End

**Purpose**: Verify all functionality works correctly

**Test Checklist**:
- [ ] Video generation: Wan 2.7 T2V with text prompt
- [ ] Video generation: Wan 2.5 I2V with image + prompt
- [ ] Video generation: Seedance 2.0 with advanced parameters
- [ ] 3D generation: Hunyuan3D 2.0 with text prompt
- [ ] 3D generation: Hunyuan3D 2.0 with image
- [ ] 3D generation: TRELLIS 2 with image
- [ ] History tab: Statistics display correctly
- [ ] History tab: Recent generations table shows all entries
- [ ] Cost tracking: Costs calculated and displayed correctly
- [ ] Download buttons: All outputs downloadable
- [ ] Error handling: Invalid inputs show clear errors

**Cost Estimate for Full Testing**: ~$5-10 total

---

### Step 19: Performance Optimization

**Purpose**: Improve user experience during long generations

**Implementation**:
```python
# Add progress indicators
import time

def generate_with_progress(generate_func, *args, **kwargs):
    """Wrapper to show progress during generation."""
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    status_text.text("Starting generation...")
    progress_bar.progress(10)
    
    # Start generation in background
    result = generate_func(*args, **kwargs)
    
    if result["success"]:
        progress_bar.progress(100)
        status_text.text("Complete!")
        time.sleep(1)
        progress_bar.empty()
        status_text.empty()
    
    return result
```

---

### Step 20: Documentation and Cleanup

**Purpose**: Final documentation and code cleanup

**Actions**:
1. Add docstrings to all public functions
2. Run code formatter: `black lib/ app.py`
3. Run linter: `ruff check lib/ app.py`
4. Update README.md with screenshots
5. Create example usage guide
6. Verify all TODOs are completed

---

## Summary

**Total Steps**: 20
**Estimated Time**: 8-12 hours for complete implementation
**Estimated Cost for Testing**: $5-10 in Replicate API credits

**Next Action**: Start with Phase 0, Step 1

---

## Notes for Implementation

1. **Replicate Model IDs**: Verify exact model IDs on replicate.com before implementing. They may have changed.

2. **Parameter Names**: Check each model's API documentation for exact parameter names (e.g., `num_inference_steps` vs `steps`).

3. **Output Formats**: Some 3D models return multiple files (GLTF + bin + textures). Handle accordingly.

4. **model-viewer Integration**: The 3D viewer may require serving files via HTTP or using base64 encoding. Test different approaches.

5. **Error Messages**: Replicate API errors can be cryptic. Add user-friendly error mapping in `lib/utils.py`.

6. **Testing Strategy**: Test one model completely before moving to the next. Verify cost tracking works before implementing all models.
