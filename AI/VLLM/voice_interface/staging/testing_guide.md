# Voice Interface 테스트 가이드 (Phase-by-Phase)

## 공통 준비
- 위치: `AI/VLLM/voice_interface`
- 실행:
```
docker compose -f docker/compose.yml up -d --build
curl http://localhost:8010/health  # {"ok": true, "use_openai": false}
```
- OpenAI 대체 모드(서버 vLLM 미구축 시):
```
export USE_OPENAI=true
export OPENAI_API_KEY=sk-...   # 필수
export OPENAI_MODEL=gpt-4o-mini
export OPENAI_BASE_URL=https://api.openai.com/v1
```
- vLLM 모드로 복귀:
```
unset USE_OPENAI OPENAI_API_KEY OPENAI_MODEL OPENAI_BASE_URL
```

---

## STT 동작(현재)
- 서버측 STT: 클라이언트가 오디오 파일(예: WAV)을 업로드하면 서버가 faster-whisper(CPU)로 전사
- 클라이언트측 STT(향후): Flutter에서 mic 캡처→로컬 STT 또는 서버 스트리밍(STT)으로 대체 가능

---

## Phase 1: REST MVP

### 1) STT (파일 → 텍스트)
- 목적: 업로드한 WAV에서 텍스트 전사
- 명령:
```
curl -F file=@sample.wav http://localhost:8010/voice/stt
```
- 기대 결과:
```
{ "text": "...", "duration": <float> }
```
- 실패 시 체크: 파일 포맷, 무음, 로그(/app)

### 2) LLM (텍스트 → 답변)
- 목적: vLLM OpenAI 호환 `/chat/completions` 경로 검증
- 명령:
```
curl -X POST http://localhost:8010/voice/llm \
  -H "Content-Type: application/json" \
  -d '{"messages":[{"role":"user","content":"안녕"}]}'
```
- 기대 결과: `choices[0].message.content`에 텍스트
- 실패 시 체크: vLLM 로그, 모델명(VLLM_MODEL)

### 3) TTS (텍스트 → 오디오)
- 목적: 텍스트에서 WAV 생성(placeholder)
- 명령:
```
curl -X POST http://localhost:8010/voice/tts \
  -H "Content-Type: application/json" \
  -d '{"text":"안녕하세요"}' > out.wav
```
- 기대 결과: `out.wav` 재생 가능

### 4) Assistant (파일 → 오디오)
- 목적: STT→LLM→TTS 파이프라인 전체 대상
- 명령:
```
curl -F file=@sample.wav http://localhost:8010/voice/assistant > reply.wav
```
- 기대 결과: `reply.wav` 재생 가능
- 실패 시 체크: vLLM 응답 유효성, STT 결과 비어있음 여부, 로그

---

## Phase 2: WS 스트리밍(초안)
- 목적: 실시간 오디오 프레임 전송/부분 전사/응답 토큰/합성 chunk
- 준비: 브라우저/CLI(WebSocket) 클라이언트
- 접속:
```
# wscat 예시
wscat -c "ws://localhost:8010/voice/stream"
```
- 절차(초안):
  1) 연결 후 서버가 `{event:"ready"}` 전송
  2) 클라이언트가 텍스트 ping 또는 오디오 프레임 전송
  3) 서버가 `{partial_transcript: "...", final:false}` 응답(현재 스텁)
- 실패 시 체크: 포트/방화벽, 서버 로그

---

## Pytest
- 경로: `AI/VLLM/voice_interface/tests/test_api.py`
- 실행 예:
```
pytest AI/VLLM/voice_interface/tests/test_api.py -q
```
- 포함 테스트:
  - health 200
  - /voice/tts audio/wav 응답
  - /voice/assistant audio/wav (vLLM 호출 monkeypatch)

---

## 트러블슈팅
- vLLM 모델 로드 지연: 첫 요청 대기 발생 → 사전 프라이밍 요청
- 메모리/CPU 과점유: Phi-3-mini처럼 작은 모델부터, 필요 시 모델/파라미터 축소
- STT 무음: 파일 포맷/샘플레이트 확인(16kHz mono 권장)

---

## 체크리스트(요약)
- [ ] Phase 1: STT/LLM/TTS/Assistant 수동 테스트 통과
- [ ] Pytest 통과 (health/tts/assistant)
- [ ] Phase 2: WS ready/partial 이벤트 확인
