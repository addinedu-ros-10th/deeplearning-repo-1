# TTS Backend Setup (Piper / Mimic3 / OpenTTS)

## Overview
- This TTS server proxies to external TTS engines (Piper, Mimic3, OpenTTS) and exposes a stable API: `GET /api/tts?text=...&voice=...` (or Piper compatible `POST`).
- Default target: Piper with Korean voices: `ko_KR-pml_high` (recommended) and `ko_KR-pml_low`.

## Quickstart (Docker Compose)
```bash
cd server/tts_server/docker
docker compose up --build -d
# tts-backend: rhasspy/wyoming-piper (port 5002)
# tts-server: FastAPI proxy (port 5502)
```

Test:
```bash
curl -sS "http://localhost:5502/api/tts?text=안녕하세요" --output hello.wav
aplay hello.wav # or any wav player
```

### Microphone-based Manual Test with Flutter
1) Run Docker Compose for TTS backend and server
```bash
cd server/tts_server/docker
docker compose up --build -d
```

2) Configure `app/user_app/assets/env/.env.dev`
```env
TTS_BACKEND=piper
TTS_BASE_URL=http://localhost:5502
TTS_DEFAULT_VOICE=ko_KR-pml_high
```

3) Launch Flutter app (desktop or Android recommended)
```bash
cd app/user_app
flutter pub get
flutter run -d linux --dart-define=USE_DOTENV=true --dart-define=APP_ENV=dev
# or Android emulator: flutter run -d emulator-5554 --dart-define=USE_DOTENV=true --dart-define=APP_ENV=dev
# or Web (allow mic): flutter run -d chrome --dart-define=USE_DOTENV=true --dart-define=APP_ENV=dev
```

4) In-app test
- Select Backend = Piper, Voice = ko_KR-pml_high
- Tap Listen and speak Korean; then tap Ask + Speak to hear TTS

Troubleshooting
- No audio: check system volume/device; `docker compose logs -f tts-backend tts-server`
- Mic permission: allow in OS/Android/Web (Chrome)
- CORS on Web: use same-origin or add CORS middleware/proxy

## Environment Variables
- `TTS_BACKEND`: `piper` | `mimic3` | `opentts`
- `TTS_BASE_URL`: upstream base URL (e.g., `http://tts-backend:5002`)
- `TTS_DEFAULT_VOICE`: default voice id (e.g., `ko_KR-pml_high`)
- `API_PORT`: exposed FastAPI port (default 5502)

## Backend Notes
- Piper: typically `POST /api/tts?voice=...` with body `{text}` → `audio/wav`
- Mimic3/OpenTTS: `GET /api/tts?voice=...&text=...` → `audio/wav`

## Integrate with app_server
- Use `TTS_BASE_URL=http://tts-server:5502` in app_server to proxy/stream audio to clients.
- Reuse env naming conventions from `server/app_server/app/infrastructure/settings.py` where appropriate.

## DB (Optional)
- If you need logging/caching in future:
  - Read DB URL from `DB_APP_URL`.
  - Follow the same pool settings naming (`DATABASE_POOL_SIZE`, `DATABASE_MAX_OVERFLOW`).
  - Initial version does not persist.

## Monorepo Policy
- Do not edit code outside `server/tts_server` for this feature.
