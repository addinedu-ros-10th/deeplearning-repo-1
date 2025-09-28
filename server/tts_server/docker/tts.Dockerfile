FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl build-essential git cmake pkg-config libespeak-ng1 libespeak-ng-dev \
    && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

# Install Rust and Piper CLI for local testing (optional but helpful)
# Build Piper CLI from repo root (correct path)
# RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y && \
#     . /root/.cargo/env && \
#     git clone https://github.com/rhasspy/piper.git /tmp/piper && \
#     cd /tmp/piper && \
#     cargo build --release -p piper && \
#     cp target/release/piper /usr/local/bin/ && \
#     rm -rf /tmp/piper

COPY pyproject.toml /app/
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi --no-root

COPY src /app/src
ENV PYTHONPATH=/app/src

EXPOSE 5502

CMD ["uvicorn", "tts_server.main:app", "--host", "0.0.0.0", "--port", "5502"]


