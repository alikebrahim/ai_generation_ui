# IMPLEMENTATION_VER-0.8.0.md — Replicate Audio (Music + Speech)

**Version**: v0.8.0  
**Status**: Complete

**Schema/pricing snapshots** (fetched 2026-06-04, filenames unchanged):

- `IMPLEMENTATION_VER-0.9.0-replicate-api-snapshot.json`
- `IMPLEMENTATION_VER-0.9.0-pricing-scrape.json`

## Delivered

- Nine Replicate audio models in `src/audio_models_config.py` (3 music, 6 speech).
- Payload builders in `src/audio_payload.py`; generation in `src/audio_gen.py`.
- **Audio** nav segment (`?page=audio`) with workflow filter: Make music | Generate speech | All.
- `src/ui/audio_tab.py`, `src/ui/audio_forms.py`, `render_audio_result` with `st.audio()`.
- Local storage under `outputs/audio/`; History `model_type=audio`; remix to Audio tab.
- Pricing estimates in `src/pricing.py` (per file, per 1k chars/tokens, per output second).
- Registry, dry-run, and `model_diagnostics.py` probes (no paid calls).

## Models

| Slug | Replicate ID | Category |
|------|--------------|----------|
| music-2.5 | minimax/music-2.5 | music |
| stable-audio-2.5 | stability-ai/stable-audio-2.5 | music |
| lyria-2 | google/lyria-2 | music |
| realtime-tts-2 | inworld/realtime-tts-2 | speech |
| realtime-tts-1.5-max | inworld/realtime-tts-1.5-max | speech |
| speech-2.8-hd | minimax/speech-2.8-hd | speech |
| speech-2.8-turbo | minimax/speech-2.8-turbo | speech |
| chatterbox | resemble-ai/chatterbox | speech |
| elevenlabs-v3 | elevenlabs/v3 | speech |

## Next milestone

**v1.0.0** — stable Replicate-only personal baseline when behavior and docs agree through normal app use. See `ROADMAP.md`.