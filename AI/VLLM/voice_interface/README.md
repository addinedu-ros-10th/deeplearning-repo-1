# Voice Interface (STT → LLM → TTS)

vLLM(OpenAI 호환) + FastAPI 음성 API(REST/WS)로 구성된 최소 스캐폴딩입니다.

## 구조
- vLLM: 모델 서빙 (기본 8001)
- voice-api: STT/LLM/TTS REST + WS (기본 8010)

## 시작
```
cd AI/VLLM/voice_interface
# 환경 변수 확인 후
docker compose -f docker/compose.yml up -d --build
curl http://localhost:8010/health
```

## 엔드포인트
- POST /voice/stt
- POST /voice/llm
- POST /voice/tts
- POST /voice/assistant
- WS /voice/stream
