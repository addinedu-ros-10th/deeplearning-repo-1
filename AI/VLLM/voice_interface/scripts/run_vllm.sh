#!/usr/bin/env bash
set -euo pipefail
MODEL=${VLLM_MODEL:-microsoft/Phi-3-mini-4k-instruct}
PORT=${VLLM_PORT:-8001}
exec docker run --rm -p ${PORT}:${PORT} -e HF_HOME=/root/.cache/huggingface vllm/vllm-openai:latest --model ${MODEL} --device cpu --port ${PORT}
