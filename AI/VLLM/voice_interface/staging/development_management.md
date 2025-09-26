# Voice Interface 개발 관리 문서

## 1) 개요
- 목적: 노트북급 CPU 환경에서도 동작 가능한 실시간 지향 음성 인터페이스(STT → LLM → TTS) 구축
- 구성: vLLM(OpenAI 호환) + FastAPI 음성 API(REST/WS)
- 비고: 모델/자원 상황에 맞게 교체 가능한 설계(AWQ/INT4 권장)

## 2) 현재 CPU 기준(요청 사양)
- CPU: Intel Core Ultra 5 (Meteor Lake) 14C(4P+8E+2LE) / 18T
- NPU: Intel AI Boost 11 TOPS
- GPU: Intel Arc iGPU 7core @ 2.2GHz
- RAM: LPDDR5x 16GB / 7467MHz
- Disk: NVMe 512GB

## 3) 리포 구조
- `AI/VLLM/voice_interface/`
  - `docker/compose.yml`: vLLM(8001, CPU) + voice-api(8010)
  - `docker/voice.Dockerfile`: voice-api 컨테이너 정의
  - `requirements.txt`: fastapi/httpx/websockets + faster-whisper 등
  - `src/app.py`: REST/WS 스텁 및 vLLM 연동(`/chat/completions`)
  - `src/stt_transcriber.py`: faster-whisper 기반 파일 전사(CPU, int8)
  - `src/tts_synth.py`: TTS placeholder(WAV 바이트 생성)
  - `README.md`: 사용 요약
  - `staging/build_plan.md`: 구축 전략·체크리스트(Phase 진행)
  - `staging/development_management.md`: 본 문서(본 파일)
  - `staging/testing_guide.md`: 단계별 테스트 가이드
  - `scripts/run_vllm.sh`: vLLM 실행 헬퍼(cpu)

## 4) Docker Compose 서비스
- vLLM
  - image: `vllm/vllm-openai:latest`
  - env: `VLLM_MODEL`(기본 `microsoft/Phi-3-mini-4k-instruct`)
  - args: `--device cpu --port 8001`
  - port: 8001
- voice-api
  - build: `docker/voice.Dockerfile`
  - env: `VLLM_BASE_URL=http://vllm:8001/v1`
  - port: 8010

## 5) 환경 변수
- `VLLM_MODEL`: vLLM 서버에 로드할 모델명(예: `microsoft/Phi-3-mini-4k-instruct`)
- `VLLM_BASE_URL`: voice-api가 사용할 OpenAI 호환 엔드포인트(기본 `http://vllm:8001/v1`)
- `STT_MODEL`: faster-whisper 모델 사이즈(기본 `base`)

## 6) 실행 방법(로컬)
```bash
cd AI/VLLM/voice_interface
# (선택) 모델 변경
export VLLM_MODEL="microsoft/Phi-3-mini-4k-instruct"
# Compose Up
docker compose -f docker/compose.yml up -d --build
# 헬스체크
curl http://localhost:8010/health
```

## 7) 엔드포인트(MVP)
- REST
  - `POST /voice/stt`         : 파일 → 텍스트(JSON, faster-whisper)
  - `POST /voice/llm`         : 텍스트 → 답변(vLLM `/chat/completions`)
  - `POST /voice/tts`         : 텍스트 → 오디오(WAV, placeholder)
  - `POST /voice/assistant`   : 파일 → 오디오(엔드투엔드, WAV 반환)
- WS
  - `GET /voice/stream`       : 실시간 스트리밍(초안 Stub: partial 전송)

## 8) app_server WebSocket 재사용 방안
- 상위 Nginx에서 `/voice/*` → voice-api로 프록시(기존 `/ws` 업그레이드 규칙 재사용)
- 단일 게이트웨이 운영(JWT/리밋팅/로깅 일원화)

## 9) 구축 전략 & 체크리스트(요약)
- Phase 0: 스캐폴딩/설정 (완료)
  - [x] compose: vLLM(cpu)+voice-api
  - [x] env: VLLM_BASE_URL, VLLM_MODEL
- Phase 1: REST MVP (진행)
  - [x] STT: faster-whisper 파일 전사 적용
  - [x] TTS: placeholder(WAV) 통합
  - [x] /voice/assistant 오디오(WAV) 반환
  - [ ] XTTS v2(CPU) 통합 및 캐시
- Phase 2: WS 스트리밍
  - [ ] /voice/stream: 부분 전사/LLM 토큰/TTS chunk 스트림
  - [ ] 버퍼/지연 제어, 장애 시 REST 폴백
- Phase 3: 품질/가시성
  - [ ] 지연/품질 로그, 메트릭, 대시보드

## 10) 모델 추천(자원별)
- CPU: Phi-3-mini / 4-bit 7B (vLLM) 또는 llama.cpp 로컬 대체
- 노트북 GPU(4–8GB): Llama-3-8B-Instruct(AWQ/INT4), Mistral-7B(AWQ)
- STT: faster-whisper, TTS: coqui-ai/XTTS v2

## 11) 진행 로그(요약)
- 2025-09-24: 스캐폴딩 생성, vLLM CPU 구성, STT 연동, 문서/체크리스트 작성
- 2025-09-24: TTS placeholder 통합, /voice/assistant에서 WAV 반환, API 테스트 추가

## 12) 핸드오버/재개 가이드(다른 머신)
1) 종속성
- Docker, Docker Compose 설치
- 포트 가용성: 8001(vLLM), 8010(voice-api)

2) 코드 체크아웃
```bash
git clone <repo>
cd AI/VLLM/voice_interface
```

3) 모델/환경 설정
```bash
export VLLM_MODEL="microsoft/Phi-3-mini-4k-instruct"  # 또는 원하는 모델
```

4) 기동/헬스
```bash
docker compose -f docker/compose.yml up -d --build
curl http://localhost:8010/health
```

5) 기능 점검(수동)
- STT: `/voice/stt`(파일 업로드)
- LLM: `/voice/llm`(메시지 요청)
- TTS: `/voice/tts`(WAV 저장/재생)
- Assistant: `/voice/assistant`(WAV 저장/재생)

6) 테스트 (로컬)
```bash
pytest AI/VLLM/voice_interface/tests/test_api.py -q
```

7) 다음 작업
- XTTS v2 CPU 통합/캐시 → 오디오 품질 개선
- WS 스트리밍 초안 구현 및 테스트(부분 전사/토큰/TTS chunk)
- server/app_server Nginx 프록시 연동 가이드 추가
