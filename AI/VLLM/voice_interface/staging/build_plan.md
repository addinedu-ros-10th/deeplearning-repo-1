# Voice Interface 구축 전략 & 체크리스트

## 목표
- vLLM(OpenAI 호환) + FastAPI 음성 API(REST/WS)를 단순/경량 구성
- 실시간성(WS)을 지향하며, 파일 업로드 기반 REST MVP부터 단계 도입
- 모델은 머신 자원에 맞춰 교체 가능(AWQ/INT4 권장)

## 액션 체크리스트
- [x] 스캐폴딩 생성(README, compose, Dockerfile, requirements, app)
- [x] vLLM CPU 모드 구성(VLLM_MODEL=Phi-3-mini-4k-instruct)
- [x] STT(faster-whisper CPU) 기본 연동
- [ ] REST MVP 완성(LLM/TT S 파이프라인 반환 구조 정리)
- [ ] WS 스트리밍(부분 전사/토큰/합성 chunk) 초안
- [ ] 문서: 모델 가이드/성능 팁/운영 체크리스트

## 단계별 구현(Phase)
1) Phase 0: 스캐폴딩/설정 (완료)
   - compose: vLLM(8001, cpu) + voice-api(8010)
   - env: VLLM_BASE_URL, VLLM_MODEL
2) Phase 1: REST MVP (진행)
   - STT: faster-whisper 파일 전사 적용
   - LLM: vLLM /chat/completions 연동, 파라미터(temperature, max_tokens)
   - TTS: XTTS v2(우선 CPU) 및 캐시(예정)
   - /voice/assistant: 오디오→오디오 파이프라인(현재 텍스트/LLM 응답 반환)
3) Phase 2: WS 스트리밍
   - /voice/stream: 오디오 프레임 수신, partial/final STT, LLM 토큰, TTS chunk
   - 버퍼/지연 제어, 장애 시 REST 폴백
4) Phase 3: 품질/가시성
   - 구조화 로그/메트릭, 지연/품질 최적화

## server/app_server WebSocket 재사용 방안
- Nginx에서 `/voice/*`를 voice-api로 프록시해 단일 게이트웨이 구성
- 기존 `/ws` 업그레이드 규칙 재사용, 인증/리밋팅은 상위 게이트웨이에서 일원화

## 모델 추천(요약)
- CPU: phi-3-mini / 4-bit 7B (vLLM) 또는 llama.cpp 로컬 대체
- 노트북 GPU(4–8GB): Llama-3-8B-Instruct(AWQ/INT4), Mistral-7B(AWQ)
- TTS: coqui-ai/XTTS v2, STT: faster-whisper

## 참고
- README의 빠른 시작을 먼저 수행 후, Phase 1 작업부터 순차 진행하세요.
