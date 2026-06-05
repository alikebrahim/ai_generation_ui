"""Model configurations — identifiers, display names, parameter schemas.

Each ModelConfig captures:
- The Replicate model identifier (replicate_id)
- Which input modes are supported (text, image)
- Which parameters are Balanced (always visible) vs Advanced (in expander)
- Default values for all parameters
- (v0.6.6+) Grouped advanced, param help, high-impact ★, and named presets (creative
  starting points) for better discoverability of model capabilities.
"""

# Re-export the supporting types (and ModelConfig) so the public surface of
# `from src.models_config import ModelConfig, ModelType, ...` remains 100%
# unchanged after moving the dataclass definition to domain.py for cycle
# breaking. The aliases are not referenced by name in the remaining body of
# this file (they were only used inside the moved dataclass), hence noqa.
from src.domain import (  # noqa: F401
    ModelConfig,
    ModelType,
    ParamConstraint,
    ProviderEndpointMode,
    ProviderName,
    WorkflowArchetype,
)

# ModelConfig (and the supporting type aliases + ParamConstraint) live in
# src/domain.py. This breaks the circular import with src/audio_models_config.py
# (which only needs the dataclass to construct its 9 audio models) while
# models_config.py still does the bottom `from ...audio... import AUDIO_MODELS`
# and builds ALL_MODELS. The names are re-exported here so that every caller
# using `from src.models_config import ModelConfig, VIDEO_MODELS, ...` (and the
# get_* helpers) continues to work with zero changes.

# ═══════════════════════════════════════════════
#  VIDEO MODELS
# ═══════════════════════════════════════════════

_VIDEO_FILE_TYPES = ["mp4", "mov", "webm"]
_IMAGE_FILE_TYPES = ["png", "jpg", "jpeg", "webp"]

WAN_2_7_T2V = ModelConfig(
    name="wan-2.7-t2v",
    display_name="Wan 2.7 T2V",
    model_type="video",
    replicate_id="wan-video/wan-2.7-t2v",
    supports_text=True,
    supports_image=False,
    supports_audio=True,  # accepts audio uri for synchronization
    requires_text=True,
    provider="replicate",
    provider_model_id="wan-video/wan-2.7-t2v",
    provider_endpoint="versionless",
    workflow_archetype="text_or_image_video",
    workflow_tags=["text_to_video"],
    media_roles={
        "prompt": "Prompt",
    },
    balanced_params=[
        "prompt",
        "duration",
        "aspect_ratio",
        "seed",
        "resolution",
    ],
    advanced_params=[
        "negative_prompt",
        "enable_prompt_expansion",
    ],
    defaults={
        "duration": 5,
        "resolution": "1080p",
        "aspect_ratio": "16:9",
        "seed": -1,
        "enable_prompt_expansion": True,
        "negative_prompt": "",
    },
    param_constraints={
        "duration": {"min": 2, "max": 15, "ui_type": "slider"},
        "resolution": {"enum": ["720p", "1080p"], "ui_type": "dropdown"},
        "aspect_ratio": {
            "enum": ["16:9", "9:16", "1:1", "4:3", "3:4"],
            "ui_type": "dropdown",
        },
        "seed": {"nullable": True},
    },
    metadata_verified_date="2026-06-04",
    replicate_page_url="https://replicate.com/wan-video/wan-2.7-t2v",
    pricing_notes=(
        "~$0.10/s output video (Replicate page); table uses per-second estimate."
    ),
    output_notes="Single video URI.",
)

WAN_2_5_I2V = ModelConfig(
    name="wan-2.5-i2v-fast",
    display_name="Wan 2.5 I2V Fast",
    model_type="video",
    replicate_id="wan-video/wan-2.5-i2v-fast",
    supports_text=True,
    supports_image=True,
    supports_audio=True,
    requires_text=True,
    requires_image=True,
    provider="replicate",
    provider_model_id="wan-video/wan-2.5-i2v-fast",
    provider_endpoint="versionless",
    workflow_archetype="text_or_image_video",
    workflow_tags=["image_to_video"],
    media_roles={
        "prompt": "Prompt",
        "image": "Start frame image",
    },
    balanced_params=[
        "prompt",
        "image",
        "duration",
        "seed",
        "resolution",
    ],
    advanced_params=[
        "negative_prompt",
        "enable_prompt_expansion",
    ],
    defaults={
        "duration": 5,
        "resolution": "720p",
        "seed": -1,
        "enable_prompt_expansion": True,
        "negative_prompt": "",
    },
    param_constraints={
        "duration": {"enum": [5, 10], "ui_type": "dropdown"},
        "resolution": {"enum": ["720p", "1080p"], "ui_type": "dropdown"},
        "seed": {"nullable": True},
    },
    metadata_verified_date="2026-06-04",
    replicate_page_url="https://replicate.com/wan-video/wan-2.5-i2v-fast",
    pricing_notes=(
        "Approx per-second output pricing; verify on Replicate before trusting."
    ),
    output_notes="Single video URI.",
)

SEEDANCE_2_0 = ModelConfig(
    name="seedance-2.0",
    display_name="Seedance 2.0",
    model_type="video",
    replicate_id="bytedance/seedance-2.0",
    supports_text=True,
    supports_image=True,
    supports_audio=True,
    requires_text=True,
    provider="replicate",
    provider_model_id="bytedance/seedance-2.0",
    provider_endpoint="versionless",
    workflow_archetype="multimodal_video",
    workflow_tags=["text_to_video", "image_to_video", "multimodal"],
    media_roles={
        "prompt": "Prompt",
        "image": "Start frame image",
        "last_frame_image": "End frame image",
        "reference_images": "Reference image",
        "reference_videos": "Reference video",
        "reference_audios": "Reference audio",
    },
    mutual_exclusion=[
        ("image", "reference_images"),
        ("last_frame_image", "reference_images"),
    ],
    balanced_params=[
        "prompt",
        "image",
        "duration",
        "aspect_ratio",
        "seed",
        "resolution",
    ],
    advanced_params=[
        "generate_audio",
        "reference_images",
        "reference_videos",
        "reference_audios",
    ],
    defaults={
        "duration": 5,
        "resolution": "720p",
        "aspect_ratio": "16:9",
        "seed": -1,
        "generate_audio": True,
        "reference_images": [],
        "reference_videos": [],
        "reference_audios": [],
    },
    param_constraints={
        "duration": {"min": -1, "max": 15, "ui_type": "slider"},
        "resolution": {"enum": ["480p", "720p", "1080p"], "ui_type": "dropdown"},
        "aspect_ratio": {
            "enum": [
                "16:9",
                "4:3",
                "1:1",
                "3:4",
                "9:16",
                "21:9",
                "9:21",
                "adaptive",
            ],
            "ui_type": "dropdown",
        },
        "seed": {"nullable": True},
        "image": {"nullable": True},
        "prompt": {"max": 4000},
    },
    param_help={
        "generate_audio": "Let the model generate matching audio (may cost more).",
        "reference_images": "Style/subject refs. Tag in prompt (e.g. [Image1]).",
        "reference_videos": "Motion/style clips. Prompt tagging usually required.",
        "reference_audios": "Audio refs for sync or style.",
    },
    file_input_params={
        "image": _IMAGE_FILE_TYPES,
        "last_frame_image": _IMAGE_FILE_TYPES,
        "reference_images": _IMAGE_FILE_TYPES,
        "reference_videos": _VIDEO_FILE_TYPES,
        "reference_audios": ["mp3", "wav", "m4a", "aac"],
    },
    high_impact_params=["generate_audio"],
    presets={
        "Fast T2V no audio": {
            "duration": 5,
            "resolution": "720p",
            "generate_audio": False,
        },
        "Balanced": {
            "duration": 5,
            "resolution": "720p",
            "aspect_ratio": "16:9",
            "generate_audio": True,
        },
        "High res + audio": {
            "duration": 8,
            "resolution": "1080p",
            "generate_audio": True,
        },
        "With end frame": {
            "duration": 5,
            "generate_audio": True,
            "last_frame_image": None,  # user still uploads
        },
    },
    metadata_verified_date="2026-06-04",
    replicate_page_url="https://replicate.com/bytedance/seedance-2.0",
    pricing_notes="Approx $0.15/s output; prompt max 4000 chars on Replicate.",
    output_notes="Single video URI; optional image for I2V.",
)

HAPPYHORSE_1_0 = ModelConfig(
    name="happyhorse-1.0",
    display_name="Happy Horse 1.0",
    model_type="video",
    replicate_id="alibaba/happyhorse-1.0",
    supports_text=True,
    supports_image=True,
    provider="replicate",
    provider_model_id="alibaba/happyhorse-1.0",
    provider_endpoint="versionless",
    workflow_archetype="text_or_image_video",
    workflow_tags=["text_to_video", "image_to_video"],
    generation_modes=[
        ("text", "Text description"),
        ("image", "Animate a start image"),
    ],
    default_generation_mode="text",
    media_roles={
        "prompt": "Prompt",
        "image": "Start frame image",
    },
    balanced_params=["prompt", "duration", "resolution", "aspect_ratio", "seed"],
    advanced_params=[],
    defaults={
        "duration": 5,
        "resolution": "1080p",
        "aspect_ratio": "16:9",
        "seed": -1,
    },
    param_constraints={
        "duration": {
            "enum": [3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15],
            "ui_type": "dropdown",
        },
        "resolution": {"enum": ["720p", "1080p"], "ui_type": "dropdown"},
        "aspect_ratio": {
            "enum": ["16:9", "9:16", "1:1", "4:3", "3:4"],
            "ui_type": "dropdown",
        },
        "seed": {"nullable": True},
        "prompt": {"max": 2500},
        "image": {"nullable": True},
    },
    required_one_of=[("prompt", "image")],
    file_input_params={"image": _IMAGE_FILE_TYPES},
    metadata_verified_date="2026-06-04",
    replicate_page_url="https://replicate.com/alibaba/happyhorse-1.0",
    pricing_notes="720p $0.14/s; 1080p $0.28/s output (Replicate page).",
    output_notes="Single video URI; T2V or I2V from one image.",
)

GEN_4_5 = ModelConfig(
    name="gen-4.5",
    display_name="Runway Gen-4.5",
    model_type="video",
    replicate_id="runwayml/gen-4.5",
    supports_text=True,
    supports_image=True,
    requires_text=True,
    provider="replicate",
    provider_model_id="runwayml/gen-4.5",
    provider_endpoint="versionless",
    workflow_archetype="text_or_image_video",
    workflow_tags=["text_to_video", "image_to_video"],
    media_roles={
        "prompt": "Prompt",
        "image": "Start frame image",
    },
    balanced_params=["prompt", "duration", "aspect_ratio", "seed"],
    advanced_params=[],
    defaults={
        "duration": 5,
        "aspect_ratio": "16:9",
        "seed": None,
    },
    param_constraints={
        "duration": {"enum": [5, 10], "ui_type": "dropdown"},
        "aspect_ratio": {
            "enum": ["16:9", "9:16", "4:3", "3:4", "1:1", "21:9"],
            "ui_type": "dropdown",
        },
        "seed": {"nullable": True},
        "image": {"nullable": True},
    },
    file_input_params={"image": _IMAGE_FILE_TYPES},
    metadata_verified_date="2026-06-04",
    replicate_page_url="https://replicate.com/runwayml/gen-4.5",
    pricing_notes="$0.12/s output (Replicate page).",
    output_notes="Single video URI; duration 5s or 10s only.",
)

SEEDANCE_2_0_FAST = ModelConfig(
    name="seedance-2.0-fast",
    display_name="Seedance 2.0 Fast",
    model_type="video",
    replicate_id="bytedance/seedance-2.0-fast",
    supports_text=True,
    supports_image=True,
    supports_audio=True,
    requires_text=True,
    provider="replicate",
    provider_model_id="bytedance/seedance-2.0-fast",
    provider_endpoint="versionless",
    workflow_archetype="multimodal_video",
    workflow_tags=["text_to_video", "image_to_video", "multimodal"],
    media_roles={
        "prompt": "Prompt",
        "image": "Start frame image",
        "last_frame_image": "End frame image",
        "reference_images": "Reference image",
        "reference_videos": "Reference video",
        "reference_audios": "Reference audio",
    },
    balanced_params=[
        "prompt",
        "duration",
        "resolution",
        "aspect_ratio",
        "seed",
        "generate_audio",
    ],
    advanced_params=[
        "image",
        "last_frame_image",
        "reference_images",
        "reference_videos",
        "reference_audios",
    ],
    defaults={
        "duration": 5,
        "resolution": "720p",
        "aspect_ratio": "16:9",
        "seed": None,
        "generate_audio": True,
        "reference_images": [],
        "reference_videos": [],
        "reference_audios": [],
    },
    param_constraints={
        "duration": {"min": -1, "max": 15, "ui_type": "slider"},
        "resolution": {"enum": ["480p", "720p"], "ui_type": "dropdown"},
        "aspect_ratio": {
            "enum": [
                "16:9",
                "4:3",
                "1:1",
                "3:4",
                "9:16",
                "21:9",
                "9:21",
                "adaptive",
            ],
            "ui_type": "dropdown",
        },
        "seed": {"nullable": True},
        "image": {"nullable": True},
        "last_frame_image": {"nullable": True},
    },
    mutual_exclusion=[
        ("image", "reference_images"),
        ("last_frame_image", "reference_images"),
    ],
    file_input_params={
        "image": _IMAGE_FILE_TYPES,
        "last_frame_image": _IMAGE_FILE_TYPES,
        "reference_images": _IMAGE_FILE_TYPES,
        "reference_videos": _VIDEO_FILE_TYPES,
        "reference_audios": ["mp3", "wav", "m4a", "aac"],
    },
    param_help={
        "generate_audio": "Generate audio track with the video.",
        "reference_images": "Style/subject refs (tag in prompt per model docs).",
    },
    high_impact_params=["generate_audio"],
    metadata_verified_date="2026-06-04",
    replicate_page_url="https://replicate.com/bytedance/seedance-2.0-fast",
    pricing_notes="$0.07–0.17/s output depending on resolution and video refs.",
    output_notes="Faster Seedance variant; 480p/720p only.",
)

KLING_V3_OMNI = ModelConfig(
    name="kling-v3-omni",
    display_name="Kling 3 Omni Video",
    model_type="video",
    replicate_id="kwaivgi/kling-v3-omni-video",
    supports_text=True,
    supports_image=True,
    requires_text=True,
    provider="replicate",
    provider_model_id="kwaivgi/kling-v3-omni-video",
    provider_endpoint="versionless",
    workflow_archetype="multimodal_video",
    workflow_tags=["text_to_video", "image_to_video", "edit_video", "multimodal"],
    media_roles={
        "prompt": "Prompt",
        "start_image": "Start frame image",
        "end_image": "End frame image",
        "reference_images": "Reference image",
        "reference_video": "Reference or source video",
    },
    balanced_params=[
        "prompt",
        "mode",
        "duration",
        "aspect_ratio",
        "generate_audio",
    ],
    advanced_params=[
        "start_image",
        "end_image",
        "reference_images",
        "reference_video",
        "video_reference_type",
        "keep_original_sound",
        "multi_prompt",
    ],
    defaults={
        "mode": "pro",
        "duration": 5,
        "aspect_ratio": "16:9",
        "generate_audio": False,
        "keep_original_sound": True,
        "video_reference_type": "feature",
        "multi_prompt": None,
    },
    param_constraints={
        "mode": {"enum": ["standard", "pro", "4k"], "ui_type": "dropdown"},
        "duration": {"min": 3, "max": 15, "ui_type": "slider"},
        "aspect_ratio": {"enum": ["16:9", "9:16", "1:1"], "ui_type": "dropdown"},
        "video_reference_type": {
            "enum": ["feature", "base"],
            "ui_type": "dropdown",
        },
        "prompt": {"max": 2500},
        "start_image": {"nullable": True},
        "end_image": {"nullable": True},
        "reference_video": {"nullable": True},
        "reference_images": {"nullable": True},
        "multi_prompt": {"nullable": True},
    },
    mutual_exclusion=[("generate_audio", "reference_video")],
    file_input_params={
        "start_image": _IMAGE_FILE_TYPES,
        "end_image": _IMAGE_FILE_TYPES,
        "reference_images": _IMAGE_FILE_TYPES,
        "reference_video": _VIDEO_FILE_TYPES,
    },
    param_help={
        "mode": "standard=fast; pro=higher quality; 4k=max res (no ref video).",
        "video_reference_type": "feature=guidance; base=source for edit.",
        "multi_prompt": "Extra structured prompts (see model card).",
        "keep_original_sound": "Preserve audio from reference video.",
    },
    high_impact_params=["mode"],
    presets={
        "Fast / cheap": {
            "mode": "standard",
            "duration": 5,
            "generate_audio": False,
            "video_reference_type": "feature",
        },
        "Balanced pro": {
            "mode": "pro",
            "duration": 5,
            "aspect_ratio": "16:9",
            "generate_audio": False,
        },
        "High quality + audio": {
            "mode": "pro",
            "duration": 8,
            "generate_audio": True,
            "keep_original_sound": False,
        },
        "4K cinematic": {
            "mode": "4k",
            "duration": 5,
            "aspect_ratio": "16:9",
            "generate_audio": False,
        },
    },
    metadata_verified_date="2026-06-04",
    replicate_page_url="https://replicate.com/kwaivgi/kling-v3-omni-video",
    pricing_notes="$0.168–$0.42/s output by mode and audio (Replicate page).",
    output_notes="Multimodal T2V/I2V/edit; 4k mode excludes reference video.",
)

DREAMACTOR_M2_0 = ModelConfig(
    name="dreamactor-m2.0",
    display_name="Dreamactor M2.0",
    model_type="video",
    replicate_id="bytedance/dreamactor-m2.0",
    supports_text=False,
    supports_image=True,
    requires_image=True,
    provider="replicate",
    provider_model_id="bytedance/dreamactor-m2.0",
    provider_endpoint="versionless",
    workflow_archetype="motion_transfer",
    workflow_tags=["motion_transfer"],
    media_roles={
        "image": "Character image",
        "video": "Driving video",
    },
    balanced_params=["cut_first_second"],
    advanced_params=[],
    defaults={"cut_first_second": True},
    param_constraints={
        "cut_first_second": {"ui_type": "checkbox"},
    },
    file_input_params={
        "image": ["png", "jpg", "jpeg"],
        "video": _VIDEO_FILE_TYPES,
    },
    required_file_params=["image", "video"],
    metadata_verified_date="2026-06-04",
    replicate_page_url="https://replicate.com/bytedance/dreamactor-m2.0",
    pricing_notes="$0.05/s output (Replicate page).",
    output_notes="Motion from driving video applied to character image.",
)

ALEPH_2 = ModelConfig(
    name="aleph-2",
    display_name="Runway Aleph 2.0",
    model_type="video",
    replicate_id="runwayml/aleph-2",
    supports_text=True,
    supports_image=False,
    requires_text=True,
    provider="replicate",
    provider_model_id="runwayml/aleph-2",
    provider_endpoint="versionless",
    workflow_archetype="video_edit",
    workflow_tags=["edit_video"],
    media_roles={
        "prompt": "Edit instructions",
        "video": "Source video",
    },
    balanced_params=["prompt", "seed"],
    advanced_params=[],
    defaults={"seed": None},
    param_constraints={
        "seed": {"nullable": True},
    },
    file_input_params={"video": _VIDEO_FILE_TYPES},
    required_file_params=["video"],
    metadata_verified_date="2026-06-04",
    replicate_page_url="https://replicate.com/runwayml/aleph-2",
    pricing_notes="$0.336/s output; early-access model (Replicate page).",
    output_notes="Edit uploaded clip (2–30s, ≤16MB); keyframes deferred in UI.",
)

KLING_V3_MOTION = ModelConfig(
    name="kling-v3-motion",
    display_name="Kling 3 Motion Control",
    model_type="video",
    replicate_id="kwaivgi/kling-v3-motion-control",
    supports_text=True,
    supports_image=True,
    requires_image=True,
    provider="replicate",
    provider_model_id="kwaivgi/kling-v3-motion-control",
    provider_endpoint="versionless",
    workflow_archetype="motion_transfer",
    workflow_tags=["motion_transfer"],
    media_roles={
        "image": "Character image",
        "video": "Driving video",
        "prompt": "Optional prompt",
    },
    balanced_params=["mode", "character_orientation", "keep_original_sound"],
    advanced_params=["prompt"],
    defaults={
        "mode": "pro",
        "character_orientation": "image",
        "keep_original_sound": True,
        "prompt": "",
    },
    param_constraints={
        "mode": {"enum": ["std", "pro"], "ui_type": "dropdown"},
        "character_orientation": {
            "enum": ["image", "video"],
            "ui_type": "dropdown",
        },
    },
    file_input_params={
        "image": _IMAGE_FILE_TYPES,
        "video": _VIDEO_FILE_TYPES,
    },
    required_file_params=["image", "video"],
    param_help={
        "mode": "pro usually better motion quality.",
        "character_orientation": "Driving video or character image sets facing.",
        "keep_original_sound": "Preserve audio from driving video.",
    },
    metadata_verified_date="2026-06-04",
    replicate_page_url="https://replicate.com/kwaivgi/kling-v3-motion-control",
    pricing_notes="$0.07/s (std), $0.12/s (pro) output.",
    output_notes="Transfer motion from reference video to character image.",
)

KLING_O1 = ModelConfig(
    name="kling-o1",
    display_name="Kling O1",
    model_type="video",
    replicate_id="kwaivgi/kling-o1",
    supports_text=True,
    supports_image=True,
    requires_text=True,
    provider="replicate",
    provider_model_id="kwaivgi/kling-o1",
    provider_endpoint="versionless",
    workflow_archetype="multimodal_video",
    workflow_tags=["text_to_video", "image_to_video", "edit_video", "multimodal"],
    media_roles={
        "prompt": "Prompt",
        "start_image": "Start frame image",
        "end_image": "End frame image",
        "reference_images": "Reference image",
        "reference_video": "Reference or source video",
    },
    balanced_params=[
        "prompt",
        "mode",
        "duration",
        "aspect_ratio",
        "video_reference_type",
    ],
    advanced_params=[
        "start_image",
        "end_image",
        "reference_images",
        "reference_video",
        "keep_original_sound",
    ],
    defaults={
        "mode": "pro",
        "duration": 5,
        "aspect_ratio": "16:9",
        "video_reference_type": "feature",
        "keep_original_sound": True,
    },
    param_constraints={
        "mode": {"enum": ["std", "pro"], "ui_type": "dropdown"},
        "duration": {"enum": [3, 4, 5, 6, 7, 8, 9, 10], "ui_type": "dropdown"},
        "aspect_ratio": {"enum": ["16:9", "9:16", "1:1"], "ui_type": "dropdown"},
        "video_reference_type": {
            "enum": ["feature", "base"],
            "ui_type": "dropdown",
        },
        "start_image": {"nullable": True},
        "end_image": {"nullable": True},
        "reference_video": {"nullable": True},
        "reference_images": {"nullable": True},
    },
    file_input_params={
        "start_image": _IMAGE_FILE_TYPES,
        "end_image": _IMAGE_FILE_TYPES,
        "reference_images": _IMAGE_FILE_TYPES,
        "reference_video": _VIDEO_FILE_TYPES,
    },
    param_help={
        "mode": "std vs pro quality tier.",
        "video_reference_type": "feature=guidance; base=edit source video.",
    },
    high_impact_params=["mode"],
    metadata_verified_date="2026-06-04",
    replicate_page_url="https://replicate.com/kwaivgi/kling-o1",
    pricing_notes="$0.084–$0.168/s output by mode and video input.",
    output_notes="NL video edit or multimodal generation via reference_video type.",
)


# ═══════════════════════════════════════════════
#  3D MODELS
# ═══════════════════════════════════════════════

HUNYUAN3D_2 = ModelConfig(
    name="hunyuan3d-2",
    display_name="Hunyuan3D 2.0",
    model_type="3d",
    replicate_id="tencent/hunyuan3d-2",
    supports_text=False,  # NOTE: Replicate schema shows image-only
    supports_image=True,
    requires_image=True,
    provider="replicate",
    provider_model_id="tencent/hunyuan3d-2",
    provider_endpoint="versioned",
    media_roles={
        "image": "Subject image",
    },
    workflow_tags=["image_to_3d"],
    balanced_params=[
        "image",
        "seed",
    ],
    advanced_params=[
        "steps",
        "guidance_scale",
        "octree_resolution",
        "remove_background",
    ],
    defaults={
        "seed": 1234,
        "steps": 50,
        "guidance_scale": 5.5,
        "octree_resolution": 256,
        "remove_background": True,
    },
    param_constraints={
        "steps": {"min": 20, "max": 50, "ui_type": "number"},
        "guidance_scale": {"min": 1.0, "max": 20.0, "ui_type": "number"},
        "octree_resolution": {"enum": [256, 384, 512], "ui_type": "dropdown"},
    },
    param_help={
        "steps": "Inference steps. Higher improves quality (plateau ~40).",
        "guidance_scale": "Prompt vs creativity. 5-8 typical for 3D.",
        "octree_resolution": "Voxel res (256 fast; 512 sharper/heavier).",
        "remove_background": "Auto-remove bg from input for clean subject.",
    },
    high_impact_params=["steps", "guidance_scale", "octree_resolution"],
    presets={
        "Fast": {
            "steps": 20,
            "guidance_scale": 3.0,
            "octree_resolution": 256,
            "remove_background": True,
        },
        "Balanced": {
            "steps": 50,
            "guidance_scale": 5.5,
            "octree_resolution": 256,
            "remove_background": True,
        },
        "High quality": {
            "steps": 50,
            "guidance_scale": 8.0,
            "octree_resolution": 512,
            "remove_background": True,
        },
    },
    metadata_verified_date="2026-06-04",
    replicate_page_url="https://replicate.com/tencent/hunyuan3d-2",
    pricing_notes="L40S compute-time estimate from pricing table.",
    output_notes="Object output with mesh field.",
)

TRELLIS_2 = ModelConfig(
    name="trellis-2",
    display_name="TRELLIS 2",
    model_type="3d",
    replicate_id="fishwowater/trellis2",
    supports_text=False,
    supports_image=True,
    requires_image=True,
    provider="replicate",
    provider_model_id="fishwowater/trellis2",
    provider_endpoint="versioned",
    media_roles={
        "image": "Subject image",
    },
    workflow_tags=["image_to_3d"],
    balanced_params=[
        "image",
        "seed",
        "pipeline_type",
    ],
    advanced_params=[
        "generate_model",
        "generate_video",
        "texture_size",
        "decimation_target",
        "preprocess_image",
        "sparse_structure_steps",
        "shape_slat_steps",
        "tex_slat_steps",
        "shape_slat_guidance_strength",
        "tex_slat_guidance_strength",
    ],
    advanced_param_groups=[
        ("Toggles", ["generate_model", "generate_video", "preprocess_image"]),
        (
            "Quality & steps",
            [
                "pipeline_type",
                "sparse_structure_steps",
                "shape_slat_steps",
                "tex_slat_steps",
                "shape_slat_guidance_strength",
                "tex_slat_guidance_strength",
            ],
        ),
        ("Mesh & texture", ["texture_size", "decimation_target"]),
    ],
    defaults={
        "seed": 42,
        "pipeline_type": "1024_cascade",
        "generate_model": True,
        "generate_video": True,
        "texture_size": 4096,
        "decimation_target": 1_000_000,
        "preprocess_image": True,
        "sparse_structure_steps": 12,
        "shape_slat_steps": 12,
        "tex_slat_steps": 12,
        "shape_slat_guidance_strength": 7.5,
        "tex_slat_guidance_strength": 1.0,
    },
    param_constraints={
        "pipeline_type": {
            "enum": ["512", "1024", "1024_cascade", "1536_cascade"],
            "ui_type": "dropdown",
        },
        "texture_size": {"min": 1024, "max": 8192, "ui_type": "number"},
        "decimation_target": {"min": 100000, "max": 2000000, "ui_type": "number"},
        "sparse_structure_steps": {"min": 1, "max": 50, "ui_type": "number"},
        "shape_slat_steps": {"min": 1, "max": 50, "ui_type": "number"},
        "tex_slat_steps": {"min": 1, "max": 50, "ui_type": "number"},
        "shape_slat_guidance_strength": {"min": 0.0, "max": 15.0, "ui_type": "number"},
        "tex_slat_guidance_strength": {"min": 0.0, "max": 15.0, "ui_type": "number"},
    },
    param_help={
        "pipeline_type": "Higher cascade = better quality, slower/expensive.",
        "texture_size": "Higher = sharper textures, larger files, longer time.",
        "decimation_target": "Target tris after simplify. Lower = lighter files.",
        "sparse_structure_steps": "Coarse structure steps (higher helps complex).",
        "shape_slat_steps": "Shape detail refinement steps.",
        "tex_slat_steps": "Texture detail steps.",
        "shape_slat_guidance_strength": "Shape fidelity to input (higher=faithful).",
        "tex_slat_guidance_strength": "Texture adherence to prompt/image.",
    },
    high_impact_params=[
        "pipeline_type",
        "texture_size",
        "decimation_target",
        "shape_slat_guidance_strength",
    ],
    presets={
        "Fast preview": {
            "pipeline_type": "512",
            "generate_video": False,
            "texture_size": 1024,
            "decimation_target": 100_000,
            "sparse_structure_steps": 6,
            "shape_slat_steps": 6,
            "tex_slat_steps": 6,
            "shape_slat_guidance_strength": 5.0,
            "tex_slat_guidance_strength": 1.0,
        },
        "Balanced": {
            "pipeline_type": "1024_cascade",
            "generate_model": True,
            "generate_video": True,
            "texture_size": 4096,
            "decimation_target": 1_000_000,
            "sparse_structure_steps": 12,
            "shape_slat_steps": 12,
            "tex_slat_steps": 12,
            "shape_slat_guidance_strength": 7.5,
            "tex_slat_guidance_strength": 1.0,
        },
        "High quality / detail": {
            "pipeline_type": "1536_cascade",
            "texture_size": 8192,
            "decimation_target": 2_000_000,
            "sparse_structure_steps": 25,
            "shape_slat_steps": 25,
            "tex_slat_steps": 25,
            "shape_slat_guidance_strength": 10.0,
            "tex_slat_guidance_strength": 2.0,
        },
        "Low poly / stylized": {
            "pipeline_type": "1024",
            "texture_size": 2048,
            "decimation_target": 100_000,
            "sparse_structure_steps": 8,
            "shape_slat_steps": 8,
            "tex_slat_steps": 8,
            "shape_slat_guidance_strength": 4.0,
        },
    },
    metadata_verified_date="2026-06-04",
    replicate_page_url="https://replicate.com/fishwowater/trellis2",
    pricing_notes="A100-80GB compute-time estimate from pricing table.",
    output_notes="model_file + optional preview video.",
    multi_output=True,
)

HUNYUAN_3D_3_1 = ModelConfig(
    name="hunyuan-3d-3.1",
    display_name="Hunyuan 3D 3.1",
    model_type="3d",
    replicate_id="tencent/hunyuan-3d-3.1",
    supports_text=True,
    supports_image=True,
    requires_text=False,  # Either prompt or image is sufficient
    requires_image=False,  # Either prompt or image is sufficient
    provider="replicate",
    provider_model_id="tencent/hunyuan-3d-3.1",
    provider_endpoint="versionless",
    media_roles={
        "prompt": "Describe the 3D model",
        "image": "Subject image",
    },
    workflow_tags=["text_to_3d", "image_to_3d"],
    generation_modes=[
        ("text", "Create from text"),
        ("image", "Create from image"),
    ],
    default_generation_mode="text",
    balanced_params=[
        "prompt",
        "image",
        "generate_type",
        "face_count",
    ],
    advanced_params=[
        "enable_pbr",
    ],
    defaults={
        "generate_type": "Normal",
        "face_count": 500000,
        "enable_pbr": False,
    },
    param_constraints={
        "generate_type": {
            "enum": ["Normal", "Geometry"],
            "ui_type": "dropdown",
        },
        "face_count": {"min": 40000, "max": 1500000, "ui_type": "slider"},
        "prompt": {"nullable": True, "max": 1024},
        "image": {"nullable": True},
    },
    # Exactly one of prompt or image must be provided; both together is invalid.
    mutual_exclusion=[("prompt", "image")],
    required_one_of=[("prompt", "image")],
    param_help={
        "face_count": "Target faces. Higher detail = heavier files, slower use.",
        "generate_type": "Normal=textured; Geometry=pure shape (no tex).",
        "enable_pbr": "Generate PBR maps (extra compute).",
    },
    high_impact_params=["face_count"],
    presets={
        "Low poly / fast": {
            "face_count": 100_000,
            "generate_type": "Normal",
            "enable_pbr": False,
        },
        "Balanced": {
            "face_count": 500_000,
            "generate_type": "Normal",
            "enable_pbr": False,
        },
        "High detail": {
            "face_count": 1_000_000,
            "generate_type": "Normal",
            "enable_pbr": True,
        },
        "Pure geometry": {
            "face_count": 800_000,
            "generate_type": "Geometry",
            "enable_pbr": False,
        },
    },
    metadata_verified_date="2026-06-04",
    replicate_page_url="https://replicate.com/tencent/hunyuan-3d-3.1",
    pricing_notes="Replicate page: per-unit pricing (~$0.16/unit); CPU hardware.",
    output_notes="Single 3D asset URI (versionless API).",
)

HUNYUAN3D_2MV = ModelConfig(
    name="hunyuan3d-2mv",
    display_name="Hunyuan3D 2 Multiview",
    model_type="3d",
    replicate_id="tencent/hunyuan3d-2mv",
    supports_text=False,
    supports_image=False,
    requires_image=False,
    provider="replicate",
    provider_model_id="tencent/hunyuan3d-2mv",
    provider_endpoint="versioned",
    media_roles={
        "front_image": "Front view (required)",
        "back_image": "Back view (optional)",
        "left_image": "Left view (optional)",
        "right_image": "Right view (optional)",
    },
    workflow_tags=["multiview_to_3d"],
    file_input_params={
        "front_image": ["png", "jpg", "jpeg", "webp"],
        "back_image": ["png", "jpg", "jpeg", "webp"],
        "left_image": ["png", "jpg", "jpeg", "webp"],
        "right_image": ["png", "jpg", "jpeg", "webp"],
    },
    required_file_params=["front_image"],
    balanced_params=[
        "front_image",
        "file_type",
        "target_face_num",
    ],
    advanced_params=[
        "back_image",
        "left_image",
        "right_image",
        "steps",
        "guidance_scale",
        "octree_resolution",
        "num_chunks",
        "remove_background",
        "seed",
        "randomize_seed",
    ],
    defaults={
        "file_type": "glb",
        "target_face_num": 10000,
        "steps": 30,
        "guidance_scale": 5.0,
        "octree_resolution": 256,
        "num_chunks": 200000,
        "remove_background": True,
        "seed": 1234,
        "randomize_seed": True,
    },
    param_constraints={
        "file_type": {"enum": ["glb", "obj", "ply", "stl"], "ui_type": "dropdown"},
        "target_face_num": {"min": 100, "max": 1000000, "ui_type": "number"},
        "steps": {"min": 1, "max": 100, "ui_type": "number"},
        "octree_resolution": {"min": 16, "max": 512, "ui_type": "number"},
        "num_chunks": {"min": 1000, "max": 5000000, "ui_type": "number"},
    },
    param_help={
        "target_face_num": "Approx faces in final mesh (post decimation).",
        "steps": "Overall inference steps.",
        "guidance_scale": "Image prompt strength.",
        "num_chunks": "Internal chunks; higher helps detailed subjects.",
        "octree_resolution": "Internal res (higher=detail, more mem/time).",
    },
    high_impact_params=[
        "steps",
        "guidance_scale",
        "octree_resolution",
        "target_face_num",
    ],
    metadata_verified_date="2026-06-04",
    replicate_page_url="https://replicate.com/tencent/hunyuan3d-2mv",
    pricing_notes="Replicate page ~$0.14/run on L40S; time varies with settings.",
    output_notes="Single 3D mesh URI (glb/obj/ply/stl via file_type).",
)

TEXT2TEX = ModelConfig(
    name="text2tex",
    display_name="Text2Tex",
    model_type="3d",
    replicate_id="adirik/text2tex",
    supports_text=True,
    supports_image=False,
    requires_text=True,
    provider="replicate",
    provider_model_id="adirik/text2tex",
    provider_endpoint="versioned",
    media_roles={
        "prompt": "Texture description",
        "obj_file": "3D mesh file (.obj)",
    },
    workflow_tags=["texturing"],
    file_input_params={"obj_file": ["obj"]},
    required_file_params=["obj_file"],
    balanced_params=[
        "prompt",
        "obj_file",
    ],
    advanced_params=[
        "negative_prompt",
        "ddim_steps",
        "new_strength",
        "update_strength",
        "num_viewpoints",
        "viewpoint_mode",
        "update_steps",
        "update_mode",
        "seed",
    ],
    defaults={
        "negative_prompt": "",
        "ddim_steps": 50,
        "new_strength": 1.0,
        "update_strength": 0.3,
        "num_viewpoints": 36,
        "viewpoint_mode": "predefined",
        "update_steps": 20,
        "update_mode": "heuristic",
    },
    param_constraints={
        "new_strength": {"min": 0.0, "max": 1.0, "ui_type": "number"},
        "update_strength": {"min": 0.0, "max": 1.0, "ui_type": "number"},
        "num_viewpoints": {
            "enum": [1, 2, 4, 6, 12, 20, 36, 68],
            "ui_type": "dropdown",
        },
        "viewpoint_mode": {
            "enum": ["predefined", "hemisphere"],
            "ui_type": "dropdown",
        },
        "update_mode": {
            "enum": ["sequential", "heuristic", "random"],
            "ui_type": "dropdown",
        },
        "seed": {"nullable": True},
    },
    advanced_param_groups=[
        ("View sampling (quality & time)", ["num_viewpoints", "viewpoint_mode"]),
        ("Update / refinement", ["update_steps", "update_mode", "update_strength"]),
        ("Diffusion steps", ["ddim_steps", "new_strength"]),
        ("Other", ["negative_prompt", "seed"]),
    ],
    param_help={
        "ddim_steps": "Diffusion steps. Higher=better tex, more time.",
        "new_strength": "New texture vs original (1.0=full replace).",
        "update_strength": "Strength of texture update pass.",
        "num_viewpoints": "Rendered views for tex. More=coverage, slower.",
        "viewpoint_mode": "Viewpoint placement around object.",
        "update_steps": "Texture update/refinement steps.",
    },
    high_impact_params=["num_viewpoints", "ddim_steps", "new_strength"],
    presets={
        "Fast / low views": {
            "num_viewpoints": 6,
            "ddim_steps": 20,
            "new_strength": 0.8,
            "update_steps": 10,
            "update_strength": 0.2,
        },
        "Balanced": {
            "num_viewpoints": 36,
            "ddim_steps": 50,
            "new_strength": 1.0,
            "update_strength": 0.3,
            "update_steps": 20,
            "update_mode": "heuristic",
        },
        "High quality / dense": {
            "num_viewpoints": 68,
            "ddim_steps": 80,
            "new_strength": 1.0,
            "update_strength": 0.5,
            "update_steps": 40,
            "viewpoint_mode": "hemisphere",
        },
        "Stylized / loose": {
            "num_viewpoints": 12,
            "ddim_steps": 30,
            "new_strength": 1.0,
            "update_strength": 0.1,
            "viewpoint_mode": "predefined",
        },
    },
    metadata_verified_date="2026-06-04",
    replicate_page_url="https://replicate.com/adirik/text2tex",
    pricing_notes="L40S compute-time estimate; non-commercial license on model card.",
    output_notes="Textured mesh URI (.obj output).",
)

ADIRIK_TEXTURE = ModelConfig(
    name="adirik-texture",
    display_name="Adirik Texture",
    model_type="3d",
    replicate_id="adirik/texture",
    supports_text=True,
    supports_image=False,
    requires_text=False,
    provider="replicate",
    provider_model_id="adirik/texture",
    provider_endpoint="versioned",
    media_roles={
        "prompt": "Surface appearance",
        "shape_path": "Untextured mesh file",
    },
    workflow_tags=["texturing"],
    file_input_params={"shape_path": ["obj", "glb", "ply"]},
    required_file_params=["shape_path"],
    balanced_params=[
        "prompt",
        "shape_path",
        "texture_resolution",
    ],
    advanced_params=[
        "guidance_scale",
        "shape_scale",
        "seed",
        "texture_interpolation_mode",
    ],
    defaults={
        "prompt": "A next gen nascar",
        "texture_resolution": 1024,
        "guidance_scale": 10.0,
        "shape_scale": 0.6,
        "seed": 0,
        "texture_interpolation_mode": "bilinear",
    },
    param_constraints={
        "texture_resolution": {"enum": [512, 1024], "ui_type": "dropdown"},
        "guidance_scale": {"min": 0.0, "max": 20.0, "ui_type": "number"},
        "shape_scale": {"min": 0.0, "max": 1.0, "ui_type": "number"},
    },
    param_help={
        "guidance_scale": "Texture vs prompt adherence (higher = stronger).",
        "shape_scale": "Scale applied to input mesh during texturing.",
        "texture_interpolation_mode": "Texture sampling (bilinear usually fine).",
    },
    high_impact_params=["guidance_scale"],
    metadata_verified_date="2026-06-04",
    replicate_page_url="https://replicate.com/adirik/texture",
    pricing_notes="L40S compute-time estimate from pricing table.",
    output_notes="Array of textured mesh URIs (may return multiple files).",
    multi_output=True,
)

RODIN = ModelConfig(
    name="rodin",
    display_name="Rodin Gen-2",
    model_type="3d",
    replicate_id="hyper3d/rodin",
    supports_text=True,
    supports_image=False,
    requires_text=True,
    requires_image=False,
    provider="replicate",
    provider_model_id="hyper3d/rodin",
    provider_endpoint="versioned",
    media_roles={
        "prompt": "Describe the 3D model",
        "images": "Reference image (optional)",
    },
    workflow_tags=["text_to_3d"],
    generation_modes=[
        ("text", "Text only"),
        ("reference", "Text + reference image"),
    ],
    default_generation_mode="text",
    file_input_params={"images": ["png", "jpg", "jpeg", "webp"]},
    required_file_params=[],
    balanced_params=[
        "prompt",
        "quality",
        "geometry_file_format",
        "material",
        "mesh_mode",
    ],
    advanced_params=[
        "images",
        "preview_render",
        "seed",
        "use_original_alpha",
        "tapose",
    ],
    defaults={
        "quality": "medium",
        "geometry_file_format": "glb",
        "material": "PBR",
        "mesh_mode": "Quad",
        "preview_render": False,
        "use_original_alpha": False,
        "tapose": False,
        "tier": "Gen-2",
    },
    param_constraints={
        "quality": {
            "enum": ["high", "medium", "low", "extra-low"],
            "ui_type": "dropdown",
        },
        "geometry_file_format": {
            "enum": ["glb", "usdz", "fbx", "obj", "stl"],
            "ui_type": "dropdown",
        },
        "material": {"enum": ["PBR", "Shaded", "All"], "ui_type": "dropdown"},
        "mesh_mode": {"enum": ["Quad", "Raw"], "ui_type": "dropdown"},
        "seed": {"nullable": True},
    },
    param_help={
        "quality": "Higher=better geo/materials (high=slow/expensive).",
        "material": "PBR realistic; Shaded simple; All for both.",
        "mesh_mode": "Quad=clean topo; Raw=max fidelity (may need cleanup).",
        "preview_render": "Small preview render (extra time).",
        "tapose": "Experimental; usually leave off.",
    },
    high_impact_params=["quality", "material"],
    presets={
        "Fast / low quality": {
            "quality": "low",
            "preview_render": False,
            "mesh_mode": "Raw",
        },
        "Balanced (medium)": {
            "quality": "medium",
            "geometry_file_format": "glb",
            "material": "PBR",
            "mesh_mode": "Quad",
            "preview_render": False,
        },
        "High quality": {
            "quality": "high",
            "geometry_file_format": "glb",
            "material": "PBR",
            "mesh_mode": "Quad",
            "preview_render": True,
        },
        "Extra detail (slow)": {
            "quality": "high",
            "preview_render": True,
        },
    },
    metadata_verified_date="2026-06-04",
    replicate_page_url="https://replicate.com/hyper3d/rodin",
    pricing_notes="Cost unknown until verified on Replicate billing page.",
    output_notes="Single 3D asset URI.",
)


# ═══════════════════════════════════════════════
#  COLLECTIONS
# ═══════════════════════════════════════════════

VIDEO_MODELS: list[ModelConfig] = [
    WAN_2_7_T2V,
    WAN_2_5_I2V,
    SEEDANCE_2_0,
    HAPPYHORSE_1_0,
    GEN_4_5,
    SEEDANCE_2_0_FAST,
    KLING_V3_OMNI,
    DREAMACTOR_M2_0,
    ALEPH_2,
    KLING_V3_MOTION,
    KLING_O1,
]
THREED_MODELS: list[ModelConfig] = [
    HUNYUAN3D_2,
    HUNYUAN3D_2MV,
    TRELLIS_2,
    HUNYUAN_3D_3_1,
    TEXT2TEX,
    ADIRIK_TEXTURE,
    RODIN,
]

from src.audio_models_config import AUDIO_MODELS  # noqa: E402

ALL_MODELS: list[ModelConfig] = VIDEO_MODELS + THREED_MODELS + AUDIO_MODELS

_MODEL_BY_NAME: dict[str, ModelConfig] = {m.name: m for m in ALL_MODELS}
_MODEL_BY_ID: dict[str, ModelConfig] = {m.replicate_id: m for m in ALL_MODELS}


def get_model_by_name(name: str) -> ModelConfig:
    """Look up a ModelConfig by its short name slug."""
    if name not in _MODEL_BY_NAME:
        raise ValueError(f"Unknown model: {name!r}. Known: {list(_MODEL_BY_NAME)}")
    return _MODEL_BY_NAME[name]


def get_model_by_replicate_id(replicate_id: str) -> ModelConfig:
    """Look up a ModelConfig by its Replicate model identifier."""
    if replicate_id not in _MODEL_BY_ID:
        raise ValueError(f"Unknown model ID: {replicate_id!r}")
    return _MODEL_BY_ID[replicate_id]


# ── Constraint query helpers (used by app.py validation & widget renderers) ──


def get_options_for_param(model: ModelConfig, param_name: str) -> list | None:
    """Return enum options if defined in model constraints, else None."""
    c = model.param_constraints.get(param_name, {})
    enum = c.get("enum")
    return list(enum) if enum else None


def get_range_for_param(
    model: ModelConfig,
    param_name: str,
) -> tuple[int | float | None, int | float | None]:
    """Return (min, max) for a numeric parameter, or (None, None)."""
    c = model.param_constraints.get(param_name, {})
    return (c.get("min"), c.get("max"))


def is_param_nullable(model: ModelConfig, param_name: str) -> bool:
    """Return True if the parameter accepts null/None."""
    c = model.param_constraints.get(param_name, {})
    return c.get("nullable", False)
