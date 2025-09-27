FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system deps
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl build-essential && rm -rf /var/lib/apt/lists/*

# Install poetry
RUN curl -sSL https://install.python-poetry.org | python3 - && \
    ln -s /root/.local/bin/poetry /usr/local/bin/poetry

COPY pyproject.toml /app/
RUN poetry config virtualenvs.create false && poetry install --no-interaction --no-ansi

COPY src /app/src

EXPOSE 5502

CMD ["uvicorn", "tts_server.main:app", "--host", "0.0.0.0", "--port", "5502"]


