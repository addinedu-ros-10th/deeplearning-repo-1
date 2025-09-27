from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
from .settings import get_settings


app = FastAPI(title="TTS Server", version="0.1.0")
settings = get_settings()


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok", "backend": settings.tts.backend}


@app.get("/api/tts")
async def tts_api(text: str = Query(..., min_length=1), voice: str | None = None):
    voice_id = voice or settings.tts.default_voice
    backend = settings.tts.backend.lower()
    base = settings.tts.base_url.rstrip("/")

    async with httpx.AsyncClient(timeout=None) as client:
        try:
            if backend == "piper":
                # POST /api/tts?voice=...  body: { text }
                resp = await client.post(f"{base}/api/tts", params={"voice": voice_id}, json={"text": text})
            elif backend in {"mimic3", "opentts"}:
                # GET /api/tts?voice=...&text=...
                resp = await client.get(f"{base}/api/tts", params={"voice": voice_id, "text": text})
            else:
                return JSONResponse({"error": f"unsupported backend: {backend}"}, status_code=400)

            if resp.status_code >= 400:
                return JSONResponse({"error": f"upstream error {resp.status_code}"}, status_code=502)

            async def iterator():
                async for chunk in resp.aiter_bytes():
                    yield chunk

            return StreamingResponse(iterator(), media_type="audio/wav")
        except httpx.HTTPError as e:
            return JSONResponse({"error": str(e)}, status_code=502)


