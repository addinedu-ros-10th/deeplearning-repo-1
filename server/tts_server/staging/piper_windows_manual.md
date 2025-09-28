# Piper Korean Windows Manual Guide

## 목표
- Windows에서 Piper 한국어(ONNX) 모델 수동 다운로드, 로컬 합성 테스트, TTS Server/OpenTTS와의 연동까지 단계별 안내

## 요구사항
- PowerShell
- curl (Windows 10 이상 기본 제공) 또는 Git Bash

## 1) 모델 수동 다운로드 (Hugging Face)
```powershell
# PowerShell 예시: 사용자 디렉터리 하위에 보이스 폴더 생성
$voice = "kss-korean"
$root = "$HOME\\piper_voices"
New-Item -ItemType Directory -Force -Path "$root\\$voice" | Out-Null
cd "$root\\$voice"

# 모델/설정 파일 다운로드
curl -L -o "$voice.onnx"  "https://huggingface.co/neurlang/piper-onnx-kss-korean/resolve/main/$voice.onnx?download=true"
curl -L -o "$voice.onnx.json" "https://huggingface.co/neurlang/piper-onnx-kss-korean/resolve/main/$voice.onnx.json?download=true"
```

## 2) Piper 실행(옵션 1: Docker 컨테이너 내부 CLI)
- 이미 레포의 Dockerfile이 Piper CLI를 포함하도록 구성됨. 컨테이너 내부에서 테스트 가능.
```powershell
# 컨테이너가 기동된 상태에서(Compose) TTS 서버 컨테이너에 접속
# Git Bash 또는 PowerShell에서 실행
docker exec -it docker-tts-server-1 bash -lc "piper --version"

# Windows 호스트에 내려받은 모델을 컨테이너로 복사 후 테스트할 수도 있음
# (또는 compose.fixed2.yml의 voices 볼륨을 사용)
```

## 3) Piper 실행(옵션 2: Windows 네이티브 실행)
- Windows에 Rust 툴체인을 설치하고 Piper를 빌드할 수 있지만, 권장 경로는 Docker 내 CLI 사용입니다.
- 네이티브 실행을 원한다면 아래를 참고하세요.
```powershell
# Rust 설치 (https://www.rust-lang.org/tools/install)
# 설치 후 새로운 PowerShell 세션에서 cargo 사용 가능

# Piper 소스 빌드
cd $HOME
git clone https://github.com/rhasspy/piper.git
cd .\piper\piper-cli
cargo build --release

# 실행 파일 경로 예시
$exe = "$HOME\\piper\\piper-cli\\target\\release\\piper.exe"
& $exe --help
```

## 4) 로컬 합성 테스트 (Docker 컨테이너 내부 권장)
```powershell
# 컨테이너 내부에서 voices 볼륨 경로 사용 (compose.fixed2.yml 기준)
docker exec -it docker-tts-server-1 bash -lc "\
  MODEL_DIR=/data/local/voices/kss-korean && \
  piper --model \"$MODEL_DIR/kss-korean.onnx\" \
        --config \"$MODEL_DIR/kss-korean.onnx.json\" \
        --output_file /tmp/test_korean.wav \
        --text \"파이퍼 한국어 합성 테스트입니다.\""

# 결과 파일을 호스트로 복사
$cid = (docker ps --filter "name=docker-tts-server-1" -q)
docker cp "$cid:/tmp/test_korean.wav" "$HOME\\test_korean.wav"
Start-Process "$HOME\\test_korean.wav"
```

## 5) OpenTTS/TTS Server와 연동
```powershell
# 서비스 기동
cd C:\Users\sbkyo\Proejct\deeplearning-repo-1\server\tts_server\docker
# 한국어 모델 자동 다운로드 포함 구성
docker compose -f compose.fixed2.yml up -d --build

# OpenTTS 보이스 확인
curl -sS http://localhost:5500/api/voices | python -m json.tool | Select-String -Pattern "ko|kss|pml"

# TTS Server 프록시 경유 합성
curl -L "http://localhost:5502/api/tts?voice=kss-korean&text=안녕하세요" -o "$HOME\\kss.wav"
Start-Process "$HOME\\kss.wav"
```

## 6) 트러블슈팅
- Compose가 VOICE_ID 경고를 뿜는 경우: compose.fixed2.yml의 fetcher 커맨드에서 $$VAR 표기를 사용했는지 확인.
- 404/exit 22: URL/파일명 오타 확인. neurlang 경로와 파일명 일치 여부 검증.
- Piper CLI 오류: libespeak 관련 오류는 Dockerfile의 의존성 설치 상태 확인. 네이티브 Windows에서는 espeak 설치 필요.

## 7) 앱 연동 팁
- user_app의 `.env.dev`:
  - TTS_BACKEND=opentts
  - TTS_BASE_URL=http://localhost:5502
  - TTS_DEFAULT_VOICE=kss-korean
- 실제 사용 시 `/api/voices`에서 반환되는 정확한 id를 사용하세요.
