import os
from tts_server.settings import get_settings


def test_env_overrides_backend(monkeypatch):
    monkeypatch.setenv("TTS_BACKEND", "opentts")
    s = get_settings()
    assert s.tts_backend.lower() == "opentts"


def test_env_overrides_base_url(monkeypatch):
    monkeypatch.setenv("TTS_BASE_URL", "http://example:1234")
    s = get_settings()
    assert s.tts_base_url == "http://example:1234"


