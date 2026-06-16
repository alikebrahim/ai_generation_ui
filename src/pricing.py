"""Static pricing table for Replicate hardware and models.

Source: static snapshot; refresh manually when prices matter.
Prices are USD per second of compute time or output duration depending on model.
Quarterly/manual refresh is tracked in ROADMAP.md v0.7.0.
"""

# Hardware pricing ($ / second of compute)
HARDWARE_PRICING = {
    "cpu": 0.000000,  # CPU-only models are free
    "t4": 0.000275,
    "l40s": 0.000575,
    "a40": 0.000725,
    "a40-large": 0.000725,
    "a100-40gb": 0.001150,
    "a100-80gb": 0.001400,
    "h100": 0.003250,
}

# Model → hardware mapping
# Wan models: priced per second of output video ($0.10/s), not per compute second.
# For cost estimation we still use compute-time pricing because Replicate's
# predict_time reflects the time the model ran on GPU.
MODEL_HARDWARE = {
    "wan-video/wan-2.7-t2v": "a100-80gb",
    "wan-video/wan-2.5-i2v-fast": "a100-80gb",
    "bytedance/seedance-2.0": "a100-80gb",
    "bytedance/seedance-2.0-fast": "a100-80gb",
    "alibaba/happyhorse-1.0": "cpu",
    "runwayml/gen-4.5": "cpu",
    "bytedance/dreamactor-m2.0": "cpu",
    "runwayml/aleph-2": "cpu",
    "kwaivgi/kling-v3-omni-video": "cpu",
    "kwaivgi/kling-v3-motion-control": "cpu",
    "kwaivgi/kling-o1": "cpu",
    "tencent/hunyuan3d-2": "l40s",
    "tencent/hunyuan3d-2mv": "l40s",
    "fishwowater/trellis2": "a100-80gb",
    "tencent/hunyuan-3d-3.1": "cpu",  # Replicate shows CPU hardware
    "adirik/text2tex": "l40s",
    "adirik/texture": "l40s",
    "hyper3d/rodin": "l40s",
    "minimax/music-2.5": "cpu",
    "stability-ai/stable-audio-2.5": "a100-80gb",
    "google/lyria-2": "cpu",
    "inworld/realtime-tts-2": "cpu",
    "inworld/realtime-tts-1.5-max": "cpu",
    "minimax/speech-2.8-hd": "cpu",
    "minimax/speech-2.8-turbo": "cpu",
    "resemble-ai/chatterbox": "cpu",
    "elevenlabs/v3": "cpu",
    "google/nano-banana-2": "cpu",
    "black-forest-labs/flux-2-max": "cpu",
    "black-forest-labs/flux-2-pro": "cpu",
    "bytedance/seedream-4.5": "cpu",
    "google/imagen-4-ultra": "cpu",
    "bytedance/seedream-5-lite": "cpu",
    "black-forest-labs/flux-2-flex": "cpu",
    "ideogram-ai/ideogram-v3-turbo": "cpu",
    "recraft-ai/recraft-v4": "cpu",
    "recraft-ai/recraft-v4-svg": "cpu",
    "google/imagen-4-fast": "cpu",
    "black-forest-labs/flux-schnell": "cpu",
}

# Audio: flat per output file (USD)
AUDIO_PER_OUTPUT_FILE = {
    "minimax/music-2.5": 0.15,
    "stability-ai/stable-audio-2.5": 0.20,
}

# Audio: per 1000 input characters (USD)
AUDIO_PER_1K_CHARACTERS = {
    "inworld/realtime-tts-2": 0.035,
    "inworld/realtime-tts-1.5-max": 0.035,
    "resemble-ai/chatterbox": 0.025,
    "elevenlabs/v3": 0.10,
}

# Audio: per 1000 input tokens — approximated as characters for estimates
AUDIO_PER_1K_TOKENS = {
    "minimax/speech-2.8-hd": 0.10,
    "minimax/speech-2.8-turbo": 0.06,
}

# Audio: per second of output (USD)
AUDIO_PER_OUTPUT_SECOND = {
    "google/lyria-2": 0.002,
}

# Per-second video output pricing (where applicable)
# These models charge by output duration, not compute time
PER_SECOND_OUTPUT_PRICING = {
    "wan-video/wan-2.7-t2v": 0.10,  # $0.10 per second of output video
    "wan-video/wan-2.5-i2v-fast": 0.05,  # approx — exact depends on resolution
    "bytedance/seedance-2.0": 0.15,  # approx
    "bytedance/seedance-2.0-fast": 0.15,  # approx mid-tier 720p
    "alibaba/happyhorse-1.0": 0.28,  # 1080p default; 720p is $0.14/s
    "runwayml/gen-4.5": 0.12,
    "bytedance/dreamactor-m2.0": 0.05,
    "runwayml/aleph-2": 0.336,
    "kwaivgi/kling-v3-omni-video": 0.224,  # pro tier approx
    "kwaivgi/kling-v3-motion-control": 0.12,  # pro tier
    "kwaivgi/kling-o1": 0.112,  # pro tier approx
}


def get_hardware_price(model_id: str) -> float:
    """Get compute price per second for a model's hardware."""
    hardware = MODEL_HARDWARE.get(model_id, "a100-80gb")
    return HARDWARE_PRICING.get(hardware, 0.001400)


# Image: flat per output image (USD) when Replicate bills per image count
IMAGE_PER_OUTPUT = {
    "google/nano-banana-2": 0.01,
    "black-forest-labs/flux-2-max": 0.04,
    "black-forest-labs/flux-2-pro": 0.03,
    "bytedance/seedream-4.5": 0.02,
    "google/imagen-4-ultra": 0.04,
    "bytedance/seedream-5-lite": 0.02,
    "black-forest-labs/flux-2-flex": 0.05,
    "ideogram-ai/ideogram-v3-turbo": 0.006,
    "recraft-ai/recraft-v4": 0.013,
    "recraft-ai/recraft-v4-svg": 0.013,
    "google/imagen-4-fast": 0.01,
    "black-forest-labs/flux-schnell": 0.0015,
}


def calculate_cost(
    model_id: str,
    predict_time: float,
    output_duration: float | None = None,
    text_length: int = 0,
    output_count: int = 1,
) -> float:
    """Calculate estimated cost for a prediction.

    For video models that charge by output duration, uses that rate.
    Audio models use per-file, per-character, per-token, or per-output-second
    tables when available. Otherwise falls back to compute-time × hardware-rate.
    """
    if model_id in IMAGE_PER_OUTPUT:
        return IMAGE_PER_OUTPUT[model_id] * max(output_count, 1)
    if model_id in AUDIO_PER_OUTPUT_FILE:
        return AUDIO_PER_OUTPUT_FILE[model_id]
    if model_id in AUDIO_PER_1K_CHARACTERS and text_length > 0:
        return (text_length / 1000.0) * AUDIO_PER_1K_CHARACTERS[model_id]
    if model_id in AUDIO_PER_1K_TOKENS and text_length > 0:
        return (text_length / 1000.0) * AUDIO_PER_1K_TOKENS[model_id]
    if (
        model_id in AUDIO_PER_OUTPUT_SECOND
        and output_duration is not None
        and output_duration > 0
    ):
        return output_duration * AUDIO_PER_OUTPUT_SECOND[model_id]
    if (
        model_id in PER_SECOND_OUTPUT_PRICING
        and output_duration is not None
        and output_duration > 0
    ):
        return output_duration * PER_SECOND_OUTPUT_PRICING[model_id]
    return predict_time * get_hardware_price(model_id)
