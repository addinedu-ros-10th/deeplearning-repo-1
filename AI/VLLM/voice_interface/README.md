# Voice Interface (STT → LLM → TTS)

vLLM(OpenAI 호환) + FastAPI 음성 API(REST/WS)로 구성된 실시간 음성 인터페이스입니다.

## 🏗️ 구조
- **vLLM**: Qwen2.5-3B-Instruct 모델 서빙 (포트 8001)
- **voice-api**: STT/LLM/TTS REST + WebSocket API (포트 8010)

## 📦 다운로드된 모델
- **Qwen2.5-3B-Instruct** (5.8GB)
  - 위치: `./models/qwen2.5-3b-instruct/`
  - 한국어/영어 지원
  - CPU 추론 최적화

## 🚀 빠른 시작

### 1. 모델 테스트
```bash
cd AI/VLLM/voice_interface
python3 test_qwen_model.py
```

### 2. 시스템 시작
```bash
# 환경 변수 설정 (선택사항)
export VLLM_MODEL="/models/qwen2.5-3b-instruct"

# Docker Compose 실행
docker compose -f docker/compose.yml up -d --build

# 헬스체크
curl http://localhost:8010/health
curl http://localhost:8001/health
```

### 3. 통합 테스트
```bash
# 전체 파이프라인 테스트
python3 test_voice_pipeline.py

# 개별 컴포넌트 테스트
curl -X POST http://localhost:8010/voice/llm \
  -H "Content-Type: application/json" \
  -d '{"messages": [{"role": "user", "content": "안녕하세요!"}]}'
```

## 🔌 API 엔드포인트

### REST API
- **POST /voice/stt** - 음성 → 텍스트 변환
- **POST /voice/llm** - 텍스트 → LLM 응답
- **POST /voice/tts** - 텍스트 → 음성 변환  
- **POST /voice/assistant** - 음성 → 음성 (전체 파이프라인)

### WebSocket
- **WS /voice/stream** - 실시간 스트리밍 인터페이스

### vLLM OpenAI 호환 API
- **POST /v1/chat/completions** - OpenAI 호환 채팅 완료
- **GET /v1/models** - 사용 가능한 모델 목록

## 📊 성능 사양
- **CPU 추론**: Intel i5-10500H 호환
- **메모리 요구사항**: ~8GB RAM
- **응답 시간**: 2-5초 (CPU 기준)
- **동시 연결**: 최대 10개 (리소스에 따라)
