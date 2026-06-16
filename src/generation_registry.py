"""Generation registry mapping model names to handlers.

Maps each model to its current generation function so UI modules don't need
hard-coded dispatch logic.
"""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from src.audio_models_config import AUDIO_MODELS
from src.generation_pipeline import (
    generate_audio_model,
    generate_image_model,
    generate_threed_model,
    generate_video_model,
)
from src.image_models_config import IMAGE_MODELS
from src.models_config import ALL_MODELS, THREED_MODELS, VIDEO_MODELS

GenerationHandler = Callable[..., dict | None]

_HANDLER_BY_TYPE: dict[str, Callable[..., dict]] = {
    "video": generate_video_model,
    "3d": generate_threed_model,
    "audio": generate_audio_model,
    "image": generate_image_model,
}


def _make_handler(model_type: str, slug: str) -> GenerationHandler:
    runner = _HANDLER_BY_TYPE[model_type]

    def _run(progress_callback: Any = None, **kwargs: Any) -> dict:
        return runner(slug, progress_callback=progress_callback, **kwargs)

    return _run


def _build_handlers() -> dict[str, GenerationHandler]:
    handlers: dict[str, GenerationHandler] = {}
    for model in VIDEO_MODELS + THREED_MODELS + AUDIO_MODELS + IMAGE_MODELS:
        handlers[model.name] = _make_handler(model.model_type, model.name)
    return handlers


GENERATION_HANDLERS: dict[str, GenerationHandler] = _build_handlers()


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
    clean_kwargs = {k: v for k, v in kwargs.items() if not k.startswith("_")}
    return handler(**clean_kwargs)


def verify_all_models_have_handlers() -> bool:
    """Verify that every configured model has a registered handler."""
    all_models = [m.name for m in ALL_MODELS]
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
