"""Replicate input builders for audio models (music + speech)."""

from __future__ import annotations

from typing import Any


def _omit_none(**kwargs: Any) -> dict[str, Any]:
    return {k: v for k, v in kwargs.items() if v is not None}


def build_music_2_5_input(
    lyrics: str,
    prompt: str = "",
    bitrate: int = 256000,
    sample_rate: int = 44100,
    audio_format: str = "mp3",
    **_: Any,
) -> dict[str, Any]:
    return _omit_none(
        lyrics=lyrics,
        prompt=prompt or None,
        bitrate=bitrate,
        sample_rate=sample_rate,
        audio_format=audio_format,
    )


def build_stable_audio_2_5_input(
    prompt: str,
    duration: int = 30,
    seed: int | None = None,
    steps: int = 8,
    cfg_scale: float = 1,
    **_: Any,
) -> dict[str, Any]:
    return _omit_none(
        prompt=prompt,
        duration=duration,
        seed=seed,
        steps=steps,
        cfg_scale=cfg_scale,
    )


def build_lyria_2_input(
    prompt: str,
    seed: int | None = None,
    negative_prompt: str | None = None,
    **_: Any,
) -> dict[str, Any]:
    return _omit_none(
        prompt=prompt,
        seed=seed,
        negative_prompt=negative_prompt or None,
    )


def build_realtime_tts_2_input(
    text: str,
    voice_id: str = "Ashley",
    language: str = "auto",
    sample_rate: int = 48000,
    temperature: float = 0,
    audio_format: str = "mp3",
    speaking_rate: float = 0,
    text_normalization: str = "auto",
    **_: Any,
) -> dict[str, Any]:
    return _omit_none(
        text=text,
        voice_id=voice_id,
        language=language,
        sample_rate=sample_rate,
        temperature=temperature,
        audio_format=audio_format,
        speaking_rate=speaking_rate,
        text_normalization=text_normalization,
    )


def build_realtime_tts_15_max_input(**kwargs: Any) -> dict[str, Any]:
    return build_realtime_tts_2_input(**kwargs)


def build_speech_28_input(
    text: str,
    voice_id: str = "English_Wiselady",
    speed: float = 1,
    pitch: int = 0,
    volume: float = 1,
    emotion: str = "auto",
    audio_format: str = "mp3",
    bitrate: int = 128000,
    sample_rate: int = 32000,
    channel: str = "mono",
    language_boost: str = "None",
    subtitle_enable: bool = False,
    english_normalization: bool = False,
    **_: Any,
) -> dict[str, Any]:
    return _omit_none(
        text=text,
        voice_id=voice_id,
        speed=speed,
        pitch=pitch,
        volume=volume,
        emotion=emotion,
        audio_format=audio_format,
        bitrate=bitrate,
        sample_rate=sample_rate,
        channel=channel,
        language_boost=language_boost,
        subtitle_enable=subtitle_enable,
        english_normalization=english_normalization,
    )


def build_chatterbox_input(
    prompt: str,
    seed: int = 0,
    temperature: float = 0.8,
    cfg_weight: float = 0.5,
    exaggeration: float = 0.5,
    audio_prompt: str | None = None,
    **_: Any,
) -> dict[str, Any]:
    return _omit_none(
        prompt=prompt,
        seed=seed,
        temperature=temperature,
        cfg_weight=cfg_weight,
        exaggeration=exaggeration,
        audio_prompt=audio_prompt,
    )


def build_elevenlabs_v3_input(
    prompt: str,
    voice: str = "Rachel",
    speed: float = 1,
    stability: float = 0.5,
    style: float = 0,
    similarity_boost: float = 0.75,
    language_code: str = "en",
    previous_text: str = "",
    next_text: str = "",
    **_: Any,
) -> dict[str, Any]:
    return _omit_none(
        prompt=prompt,
        voice=voice,
        speed=speed,
        stability=stability,
        style=style,
        similarity_boost=similarity_boost,
        language_code=language_code,
        previous_text=previous_text or None,
        next_text=next_text or None,
    )


AUDIO_PAYLOAD_BUILDERS: dict[str, Any] = {
    "music-2.5": build_music_2_5_input,
    "stable-audio-2.5": build_stable_audio_2_5_input,
    "lyria-2": build_lyria_2_input,
    "realtime-tts-2": build_realtime_tts_2_input,
    "realtime-tts-1.5-max": build_realtime_tts_15_max_input,
    "speech-2.8-hd": build_speech_28_input,
    "speech-2.8-turbo": build_speech_28_input,
    "chatterbox": build_chatterbox_input,
    "elevenlabs-v3": build_elevenlabs_v3_input,
}
