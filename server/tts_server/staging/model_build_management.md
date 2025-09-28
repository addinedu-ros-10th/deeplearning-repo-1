# TTS 모델 구축 관리 (Piper Korean)

## 목표
- OpenTTS + Piper 한국어 모델(kss-korean 또는 ko_KR-*)을 자동 다운로드/마운트하여 즉시 합성 가능 상태 확보
- TTS Server와의 엔드투엔드 합성 테스트 및 앱 연동

## 체크리스트
- [x] voices-fetcher가 neurlang 저장소에서 모델을 다운로드하도록 compose.fixed2.yml 수정
- [x] Dockerfile에 Piper CLI를 설치하여 컨테이너 내 수동 합성 테스트 지원
- [ ] OpenTTS 기동 후 `/api/voices`에서 한국어 보이스 노출 확인
- [ ] `/api/tts?voice=<id>&text=...` 합성 wav 성공 확인
- [ ] 장애/재시도 정책, 타임아웃/로깅 설계 및 문서화
- [ ] Flutter user_app `.env.dev`의 TTS_DEFAULT_VOICE를 실제 노출 ID로 정합

## 모델 소스
- GitHub(piper-voices v1.0.0): ko_KR-kss_high / ko_KR-pml_high 등
- Hugging Face(neurlang): `neurlang/piper-onnx-kss-korean`

## 자동 다운로드(Compose)
```bash
cd server/tts_server/docker
docker compose -f compose.fixed2.yml up -d --build
```

compose.fixed2.yml의 환경변수(요약):
- BASE_URL: https://huggingface.co/neurlang/piper-onnx-kss-korean/resolve
- VOICE_VERSION: main
- VOICE_ID: kss-korean

다운로드 파일 경로(볼륨):
- voices:/voices/kss-korean/{kss-korean.onnx,kss-korean.onnx.json}

## 수동 다운로드(대안)
```bash
docker run --rm -v voices:/voices -w /voices curlimages/curl:8.10.1 sh -lc '
  set -euo pipefail
  voice=kss-korean
  mkdir -p "/voices/$voice"
  cd "/voices/$voice"
  curl -fL -o "$voice.onnx"  https://huggingface.co/neurlang/piper-onnx-kss-korean/resolve/main/$voice.onnx?download=true
  curl -fL -o "$voice.onnx.json" https://huggingface.co/neurlang/piper-onnx-kss-korean/resolve/main/$voice.onnx.json?download=true
'
```

## Piper CLI 수동 테스트
```bash
docker exec -it docker-tts-server-1 bash -lc '
  MODEL_DIR=/data/local/voices/kss-korean
  piper --model "$MODEL_DIR/kss-korean.onnx" \
        --config "$MODEL_DIR/kss-korean.onnx.json" \
        --output_file /tmp/test_korean.wav \
        --text "파이퍼 한국어 음성 합성이 성공적으로 완료되었습니다."
'
```

## OpenTTS 노출 확인 및 프록시 합성 테스트
```bash
# OpenTTS 직접 확인
curl -sS http://localhost:5500/api/voices | python -m json.tool | grep -i -E "ko|kss|pml"

# 프록시(TTS Server) 경유 합성
curl -sS "http://localhost:5502/api/tts?voice=kss-korean&text=안녕하세요" -o kss.wav
```

## 트러블슈팅
- voices-fetcher exit 22: URL 또는 파일명이 잘못되었을 가능성. BASE_URL/VOICE_VERSION/VOICE_ID 확인.
- OpenTTS가 보이스를 인식하지 않는 경우: 볼륨 마운트(`/data/local/voices:ro`) 및 폴더/확장자 확인.
- Piper CLI 실행 오류: libespeak-ng1 미설치 또는 모델 경로 오타. Dockerfile 의존성 확인.


