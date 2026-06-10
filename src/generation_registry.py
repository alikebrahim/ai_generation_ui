"""Generation registry mapping model names to handlers.

Maps each model to its current generation function so UI modules don't need
hard-coded dispatch logic.
"""

from __future__ import annotations

from typing import Any, Callable

from src import audio_gen, threed_gen, video_gen
from src.audio_models_config import AUDIO_MODELS
from src.models_config import THREED_MODELS, VIDEO_MODELS

# Type for a generation handler function
GenerationHandler = Callable[..., dict | None]


def _audio_handlers() -> dict[str, GenerationHandler]:
    handlers: dict[str, GenerationHandler] = {}

    def _make(slug: str) -> GenerationHandler:
        def _run(progress_callback: Any = None, **kw: Any) -> dict:
            return audio_gen.generate_audio_model(
                slug, progress_callback=progress_callback, **kw
            )

        return _run

    for model in AUDIO_MODELS:
        handlers[model.name] = _make(model.name)
    return handlers


# Map each model name to its generation function
GENERATION_HANDLERS: dict[str, GenerationHandler] = {
    # Video models
    "wan-2.7-t2v": video_gen.generate_wan_2_7_t2v,
    "wan-2.5-i2v-fast": video_gen.generate_wan_2_5_i2v,
    "seedance-2.0": video_gen.generate_seedance_2_0,
    **video_gen.V06_VIDEO_HANDLERS,
    # 3D models
    "hunyuan3d-2": threed_gen.generate_hunyuan3d_2,
    "hunyuan3d-2mv": threed_gen.generate_hunyuan3d_2mv,
    "trellis-2": threed_gen.generate_trellis_2,
    "hunyuan-3d-3.1": threed_gen.generate_hunyuan_3d_3_1,
    "text2tex": threed_gen.generate_text2tex,
    "adirik-texture": threed_gen.generate_adirik_texture,
    "rodin": threed_gen.generate_rodin,
    **_audio_handlers(),
}


def run_generation(model_name: str, **kwargs) -> dict | None:
    """Dispatch generation to the appropriate handler.

    Args:
        model_name: Name of the model to use for generation.
        **kwargs: Parameters to pass to the generation function.

    Returns:
        Result dict from the generation function, or None if cancelled.

    Raises:
        ValueError: If model_name is not registered.
    """
    if model_name not in GENERATION_HANDLERS:
        raise ValueError(f"Unknown model: {model_name}")

    handler = GENERATION_HANDLERS[model_name]

    # Strip internal kwargs (prefixed with _) that are consumed upstream in
    # replicate_payload.py / forms plumbing but are never meant for the handler.
    clean_kwargs = {k: v for k, v in kwargs.items() if not k.startswith("_")}

    return handler(**clean_kwargs)


def verify_all_models_have_handlers() -> bool:
    """Verify that every configured model has a registered handler.

    Returns:
        True if all models are registered, False otherwise.
    """
    all_models = [m.name for m in VIDEO_MODELS + THREED_MODELS + AUDIO_MODELS]
    unregistered = [m for m in all_models if m not in GENERATION_HANDLERS]

    if unregistered:
        print(f"⚠️  Unregistered models: {', '.join(unregistered)}")
        return False

    missing_handlers = [
        name for name in GENERATION_HANDLERS if not callable(GENERATION_HANDLERS[name])
    ]
    if missing_handlers:
        print(f"⚠️  Invalid handlers: {', '.join(missing_handlers)}")
        return False

    return True
