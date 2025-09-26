from fastapi import FastAPI, UploadFile, WebSocket, HTTPException
from fastapi.responses import JSONResponse, Response
import os
import httpx

from .stt_transcriber import transcribe_file
from .tts_synth import synth_text_to_wav_bytes

app = FastAPI(title="Voice API", version="0.1.0")
VLLM_BASE_URL = os.getenv("VLLM_BASE_URL", "http://localhost:8001/v1")
USE_OPENAI = os.getenv("USE_OPENAI", "false").lower() == "true"
OPENAI_BASE_URL = os.getenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4o-mini")


@app.get("/health")
async def health():
    return {"ok": True, "use_openai": USE_OPENAI}


@app.post("/voice/stt")
async def stt(file: UploadFile):
    data = await file.read()
    if not data:
        raise HTTPException(status_code=400, detail="empty file")
    text, dur = transcribe_file(data)
    return {"text": text, "duration": dur}


@app.post("/voice/llm")
async def llm(prompt: dict):
    if USE_OPENAI:
        if not OPENAI_API_KEY:
            raise HTTPException(status_code=400, detail="OPENAI_API_KEY required when USE_OPENAI=true")
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{OPENAI_BASE_URL}/chat/completions", headers=headers, json={
                "model": OPENAI_MODEL,
                "messages": prompt.get("messages", []),
                "max_tokens": prompt.get("max_tokens", 256),
                "temperature": prompt.get("temperature", 0.2),
            })
            return JSONResponse(status_code=resp.status_code, content=resp.json())
    else:
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
    if USE_OPENAI:
        if not OPENAI_API_KEY:
            raise HTTPException(status_code=400, detail="OPENAI_API_KEY required when USE_OPENAI=true")
        headers = {"Authorization": f"Bearer {OPENAI_API_KEY}"}
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{OPENAI_BASE_URL}/chat/completions", headers=headers, json={
                "model": OPENAI_MODEL,
                "messages": [{"role": "user", "content": text}],
                "max_tokens": 256,
                "temperature": 0.2,
            })
            data_llm = resp.json()
    else:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{VLLM_BASE_URL}/chat/completions", json={
                "model": "cpu-small",
                "messages": [{"role":"user","content": text}],
                "max_tokens": 256,
                "temperature": 0.2,
            })
            data_llm = resp.json()
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
