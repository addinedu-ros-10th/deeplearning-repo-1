from fastapi import FastAPI, Query
from fastapi.responses import StreamingResponse, JSONResponse
import httpx
from .settings import get_settings


app = FastAPI(title="TTS Server", version="0.1.0")
settings = get_settings()


@app.get("/healthz")
async def healthz() -> dict:
    return {"status": "ok", "backend": settings.tts_backend}


@app.get("/api/tts")
async def tts_api(text: str = Query(..., min_length=1), voice: str | None = None):
    voice_id = voice or settings.tts_default_voice
    backend = settings.tts_backend.lower()
    base = settings.tts_base_url.rstrip("/")

    async with httpx.AsyncClient(timeout=None) as client:
        try:
            if backend == "piper":
                # POST /api/tts?voice=...  body: { text }
                resp = await client.post(f"{base}/api/tts", params={"voice": voice_id}, json={"text": text})
            elif backend in {"mimic3", "opentts"}:
                # Prefer GET, fallback to POST for compatibility
                resp = await client.get(f"{base}/api/tts", params={"voice": voice_id, "text": text})
                if resp.status_code in (400, 404, 405):
                    resp = await client.post(
                        f"{base}/api/tts",
                        params={"voice": voice_id},
                        json={"text": text},
                    )
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


