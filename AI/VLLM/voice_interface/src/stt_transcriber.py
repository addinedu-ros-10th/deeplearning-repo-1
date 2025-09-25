from faster_whisper import WhisperModel
import os
import tempfile
from typing import Tuple

_model = None


def get_model() -> WhisperModel:
    global _model
    if _model is None:
        model_size = os.getenv("STT_MODEL", "base")
        _model = WhisperModel(model_size, device="cpu", compute_type="int8")
    return _model


def transcribe_file(file_bytes: bytes) -> Tuple[str, float]:
    model = get_model()
    with tempfile.NamedTemporaryFile(suffix=".wav", delete=True) as f:
        f.write(file_bytes)
        f.flush()
        segments, info = model.transcribe(f.name, vad_filter=True)
        text = " ".join([seg.text.strip() for seg in segments])
        return text.strip(), info.duration
