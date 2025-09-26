FROM python:3.12-slim
WORKDIR /app
COPY ./AI/VLLM/voice_interface/src /app/src
COPY ./AI/VLLM/voice_interface/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt
EXPOSE 8010
CMD ["python", "-m", "src.app"]
