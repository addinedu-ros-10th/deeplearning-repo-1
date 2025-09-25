import io
import numpy as np
import soundfile as sf


def synth_text_to_wav_bytes(text: str, sample_rate: int = 16000) -> bytes:
    # Minimal placeholder synthesis: map characters to tones
    duration_per_char = 0.05  # 50 ms
    freqs = []
    for ch in text[:200]:
        if ch.isspace():
            freqs.append(0.0)
        else:
            # map ascii code to frequency in a human-audible range
            base = 300.0
            span = 800.0
            code = float(ord(ch) % 32) / 31.0
            freqs.append(base + span * code)
    # build waveform
    samples = []
    n_per = int(sample_rate * duration_per_char)
    for f in freqs:
        t = np.linspace(0, duration_per_char, n_per, endpoint=False)
        if f <= 0.0:
            wave = np.zeros_like(t)
        else:
            wave = 0.2 * np.sin(2 * np.pi * f * t)
        samples.append(wave)
    if not samples:
        samples = [np.zeros(int(sample_rate * 0.2))]
    audio = np.concatenate(samples).astype(np.float32)
    buf = io.BytesIO()
    sf.write(buf, audio, samplerate=sample_rate, format="WAV")
    return buf.getvalue()
