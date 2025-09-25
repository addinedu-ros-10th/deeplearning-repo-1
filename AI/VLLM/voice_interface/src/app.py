from fastapi import FastAPI, UploadFile, WebSocket, HTTPException
from fastapi.responses import JSONResponse, Response
import os
import httpx

from .stt_transcriber import transcribe_file
from .tts_synth import synth_text_to_wav_bytes

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
    text = body.get("text", "")
    if not text:
        raise HTTPException(status_code=400, detail="text required")
    wav = synth_text_to_wav_bytes(text)
    return Response(content=wav, media_type="audio/wav")


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
        data_llm = resp.json()
    # extract assistant text safely
    content = None
    try:
        content = data_llm.get("choices", [{}])[0].get("message", {}).get("content", "")
    except Exception:
        content = ""
    if not content:
        content = "응답을 생성하지 못했습니다."
    wav = synth_text_to_wav_bytes(content)
    return Response(content=wav, media_type="audio/wav")


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
