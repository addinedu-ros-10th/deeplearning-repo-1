import pytest
from fastapi.testclient import TestClient
from AI.VLLM.voice_interface.src.app import app


client = TestClient(app)


def test_health():
    r = client.get("/health")
    assert r.status_code == 200
    assert r.json().get("ok") is True


def test_tts_wav():
    r = client.post("/voice/tts", json={"text": "hello"})
    assert r.status_code == 200
    assert r.headers.get("content-type") == "audio/wav"
    assert len(r.content) > 1000


def test_assistant_flow_monkeypatch(monkeypatch):
    async def fake_chat(*args, **kwargs):
        class Resp:
            status_code = 200
            def json(self_inner):
                return {"choices": [{"message": {"content": "안녕하세요"}}]}
        return Resp()
    import AI.VLLM.voice_interface.src.app as appmod
    class FakeAsyncClient:
        def __init__(self, *a, **k): pass
        async def __aenter__(self): return self
        async def __aexit__(self, exc_type, exc, tb): return False
        async def post(self, url, json):
            return await fake_chat()
    appmod.httpx.AsyncClient = FakeAsyncClient

    # small wav bytes for input
    import numpy as np, soundfile as sf, io
    sr=16000
    t=np.zeros(sr//2, dtype=np.float32)
    buf=io.BytesIO()
    sf.write(buf, t, samplerate=sr, format="WAV")
    buf.seek(0)

    files = {"file": ("a.wav", buf.getvalue(), "audio/wav")}
    r = client.post("/voice/assistant", files=files)
    assert r.status_code == 200
    assert r.headers.get("content-type") == "audio/wav"
    assert len(r.content) > 1000
