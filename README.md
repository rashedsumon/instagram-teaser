# AI Teaser Generator — Instagram Reel (9:16)

Creates cinematic 5–10 second teaser videos suitable for Instagram Reels (1080×1920, MP4 H.264). Provides:
- Local cinematic fallback generation (Ken Burns + crossfades + text + optional music).
- Placeholder for Remote AI provider integrations (insert your API logic).

## Files
- `app.py` — Streamlit app (entrypoint)
- `data_loader.py` — Downloads datasets via `kagglehub`
- `requirements.txt` — Python dependencies
- `assets/` — optional sample assets (music, placeholder images)
- `outputs/` — generated videos (gitignored)

## Quick start (local)
1. Create virtualenv with Python 3.11.0:
   ```bash
   python3.11 -m venv venv
   source venv/bin/activate
