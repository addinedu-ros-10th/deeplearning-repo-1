from fastapi import FastAPI, UploadFile, WebSocket, HTTPException
from fastapi.responses import JSONResponse
import os
import httpx

from .stt_transcriber import transcribe_file

app = FastAPI(title="Voice API", version="0.1.0")
VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:8001/v1")


@app.get("/health")
async def health():
    return {"ok": True}


@app.post("/voice/stt")
async def stt(file: UploadFile):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="empty file")
    text, dur = transcribe_file(data)
    return {"text": text, "duration": dur}


@app.post("/voice/llm")
async def llm(prompt: dict):
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(f"{VLLM_BASE_URL}/chat/completions", json={
            "model": "cpu-small",
            "messages": prompt.get("messages", []),
            "max_tokens": prompt.get("max_tokens", 256),
            "temperature": prompt.get("temperature", 0.2),
        })
        return JSONResponse(status_code=resp.status_code, content=resp.json())


@app.post("/voice/tts")
async def tts(body: dict):
    # stub: return info only
    return {"audio": None, "info": "tts stub"}


@app.post("/voice/assistant")
async def assistant(file: UploadFile):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="empty file")
    text, dur = transcribe_file(data)
    async with httpx.AsyncClient(timeout=60.0) as client:
        resp = await client.post(f"{VLLM_BASE_URL}/chat/completions", json={
            "model": "cpu-small",
            "messages": [{"role":"user","content": text}],
            "max_tokens": 256,
            "temperature": 0.2,
        })
        data = resp.json()
    return {"stt_text": text, "llm": data, "tts": None}


@app.websocket("/voice/stream")
async def voice_stream(ws: WebSocket):
    await ws.accept()
    await ws.send_json({"event": "ready"})
    try:
        while True:
            _ = await ws.receive_text()
            await ws.send_json({"partial_transcript": "...", "final": False})
    except Exception:
        await ws.close()
