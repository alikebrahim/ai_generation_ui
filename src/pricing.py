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
    "tencent/hunyuan3d-2": "l40s",
    "fishwowater/trellis2": "a100-80gb",
    "tencent/hunyuan-3d-3.1": "cpu",  # Replicate shows CPU hardware
}

# Per-second video output pricing (where applicable)
# These models charge by output duration, not compute time
PER_SECOND_OUTPUT_PRICING = {
    "wan-video/wan-2.7-t2v": 0.10,  # $0.10 per second of output video
    "wan-video/wan-2.5-i2v-fast": 0.05,  # approx — exact depends on resolution
    "bytedance/seedance-2.0": 0.15,  # approx
}


def get_hardware_price(model_id: str) -> float:
    """Get compute price per second for a model's hardware."""
    hardware = MODEL_HARDWARE.get(model_id, "a100-80gb")
    return HARDWARE_PRICING.get(hardware, 0.001400)


def calculate_cost(
    model_id: str,
    predict_time: float,
    output_duration: float = None,
) -> float:
    """Calculate estimated cost for a prediction.

    For video models that charge by output duration, uses that rate.
    Otherwise falls back to compute-time × hardware-rate.
    """
    if (
        model_id in PER_SECOND_OUTPUT_PRICING
        and output_duration is not None
        and output_duration > 0
    ):
        return output_duration * PER_SECOND_OUTPUT_PRICING[model_id]
    return predict_time * get_hardware_price(model_id)
