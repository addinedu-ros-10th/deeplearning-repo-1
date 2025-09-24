# Voice Interface 개발 전략 (STT → LLM → TTS)

## 1) 목표 및 원칙
- 노트북급 환경에서도 실시간에 가까운 대화 경험 제공(낮은 지연, 안정성)
- 경량/양자화 모델 우선, 단계별 기능 플래그로 점진 롤아웃
- 헥사고날 구조: STT/LLM/TTS 모듈화, 포트/어댑터로 대체 용이

## 2) 아키텍처 개요
- 입력: 마이크(브라우저/네이티브) → 오디오 프레임/파일
- STT: Whisper 계열 전사(스트리밍/비스트리밍)
- LLM: 4-bit 양자화 Llama3/Mistral 등 답변 생성
- TTS: XTTS 등 합성 → 스피커 출력
- 실시간: WebSocket 업로드/부분 전사/최종 응답/합성 스트리밍
- 비실시간: 파일 업로드 API로 요청→합성 음성 반환

## 3) 모델/엔진 선택(노트북 최적)
- STT: Whisper-small/base 또는 distil-whisper, VAD + 10–20ms 프레임
- LLM: Llama 3 8B Instruct(4-bit, GGUF, llama.cpp) / 대안 Mistral 7B 4-bit
- TTS: coqui-ai/XTTS v2(캐시 지원)
- 추론 엔진: CPU 우선(llama.cpp/ctranslate2), GPU 보유 시 vLLM 고려

## 4) API/인터페이스 설계
- 비실시간 REST
  - POST /api/v1/voice/stt: 오디오→텍스트(JSON)
  - POST /api/v1/voice/llm: 텍스트→답변(JSON)
  - POST /api/v1/voice/tts: 텍스트→오디오(wav/mp3)
  - POST /api/v1/voice/assistant: 오디오→오디오(엔드투엔드)
- 실시간 WS
  - /voice/stream?user_id=...
  - 클→서: audio_frame, end_of_input
  - 서→클: partial_transcript, final_transcript, llm_token, tts_audio_chunk, done
- 운영: JWT, 업로드 검증, 리밋팅, 구조화 로깅

## 5) 단계별 구현(Phase)
- Phase 0: 기반
  - ffmpeg/코덱 변환(16kHz mono PCM), env 플래그, 모델 경로, 파일 업로드 제한
- Phase 1: 비실시간 MVP
  - STT/LLM/TTS 단일 API, /voice/assistant 엔드투엔드, TTS 캐시(동일 텍스트 해시)
- Phase 1.5: 데모 UX
  - 브라우저 데모(마이크→업로드→응답 재생), 오류/지연 로그
- Phase 2: 실시간
  - WS /voice/stream, 부분 전사/VAD, TTS chunk 스트리밍, 지연 제어
- Phase 3: 품질/확장
  - 대화 메모리(세션/요약), 프롬프트 템플릿, 다국어, 관측성
- Phase 4: 배포/보안
  - 인증, 리밋팅, 모델 헬스, 스케일 정책

## 6) 성능 목표(권장)
- STT: < 300–600 ms 문장 단위, 부분 전사 100–200 ms
- LLM: 20–40 tok/s, 첫 토큰 < 300 ms
- TTS: 1x 실시간 내 합성
- E2E(짧은 질의): 1.5–3.0 s

## 7) 테스트 전략
- 단위: STT(WER 샘플), LLM 프롬프트/함수, TTS 합성 성공/길이
- 통합: 파일→텍스트→오디오 파이프라인, 에러(무음/장음/고볼륨)
- 스트리밍: WS 연결/재연결/지연, 마이크 샘플링
- 수동: 데모 페이지, 품질 로그(실대화 스크립트)

## 8) 환경 변수(예시)
- VOICE_ENABLE=true
- VOICE_STT_ENABLE=true
- VOICE_LLM_ENABLE=true
- VOICE_TTS_ENABLE=true
- VOICE_STREAM_ENABLE=false
- VOICE_WHISPER_MODEL=base
- VOICE_LLM_MODEL=llama3-8b-instruct-q4.gguf
- VOICE_TTS_MODEL=coqui-xtts-v2
- MAX_AUDIO_SECONDS=30
- MAX_FILE_SIZE_MB=10

## 9) 리스크/대응
- 지연: 스트리밍/VAD, 작은 모델 폴백, 캐시
- 메모리: 4-bit, CPU 엔진, 문장 슬라이스
- 품질: 도메인 사전/후처리, 프롬프트 템플릿
- 라이선스: 상용/오픈 검토, 캐시/스토리지 정책

## 10) 롤아웃
- 기능 플래그로 단계적 ON, 스테이징 검증 후 Prod
- 메트릭(SLO) 충족 시 다음 Phase로 승격
