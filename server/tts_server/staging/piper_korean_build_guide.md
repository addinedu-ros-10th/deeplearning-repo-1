Piper ONNX KSS Korean TTS Model : https://huggingface.co/neurlang/piper-onnx-kss-korean

정말 잘 찾으셨습니다\! 직접 $\text{Hugging Face}$에서 한국어 $\text{Piper}$ 모델을 찾는 것이 가장 확실하고 좋습니다.

사용자가 찾으신 **$\text{neurlang/piper-onnx-kss-korean}$** 모델은 $\text{ONNX}$ 형식으로 변환되어 $\text{Piper}$ 엔진에 최적화된 한국어 $\text{TTS}$ 모델입니다. 이 모델은 이전에 $\text{404}$ 오류가 발생했던 `ko_KR-kss_high` 모델을 대체할 수 있으며, 다운로드도 안정적일 것입니다.

이제 이 모델을 사용하기 위해 필요한 **Rust 설치부터 $\text{Piper}$ 테스트까지의 단계**를 안내해 드리겠습니다. $\text{Piper}$의 $\text{CLI (Command-Line Interface)}$는 $\text{Rust}$로 작성되어 있어 $\text{TTS}$ 서버를 구동하기 위한 핵심 도구입니다.

-----

## 1\. 전제 조건 및 환경 설정

현재 $\text{Docker Compose}$ 환경에서 $\text{TTS}$ 서비스를 구축하고 있으므로, $\text{Piper}$를 실행할 컨테이너 또는 빌드 환경에 \*\*$\text{Rust}$\*\*와 \*\*$\text{Piper}$ $\text{CLI}$\*\*를 설치해야 합니다.

### 🔹 $\text{TTS}$ 서버 컨테이너의 $\text{Dockerfile}$ 수정 (권장)

가장 좋은 방법은 $\text{tts-server}$ 서비스에 사용되는 $\text{Dockerfile}$에 $\text{Rust}$와 $\text{Piper}$ $\text{CLI}$를 추가하는 것입니다.

**`docker/tts.Dockerfile` (예시)**

```dockerfile
# 기존 Python 설정 (TTS 서버용)
FROM python:3.11-slim

# 필요한 패키지 설치
RUN apt-get update -y && apt-get install -y --no-install-recommends \
    curl build-essential git cmake pkg-config libespeak-ng1 \
    && rm -rf /var/lib/apt/lists/*

# Rust 설치
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Piper CLI 컴파일 및 설치
# NOTE: Rust 환경 변수를 설정한 후, 새 레이어에서 빌드를 진행합니다.
RUN git clone https://github.com/rhasspy/piper.git /tmp/piper && \
    cd /tmp/piper/piper-cli && \
    cargo build --release && \
    cp target/release/piper /usr/local/bin/ && \
    rm -rf /tmp/piper /root/.cargo

# ... (기존 Python 앱 설정 및 복사 로직 계속) ...
```

-----

## 2\. 모델 다운로드 경로 수정 (Docker Compose)

새로 찾으신 모델에 맞춰 $\text{docker-compose.yml}$의 $\text{voices-fetcher}$ 환경 변수를 수정해야 합니다. 이 모델은 $\text{rhasspy}$ 조직이 아닌 `neurlang` 조직에 있으며, 경로 구조가 다릅니다.

### 🔹 `compose.fixed2.yml` 수정

`voices-fetcher` 서비스의 환경 변수를 다음과 같이 수정합니다.

| 환경 변수 | 이전 값 | 새 값 | 설명 |
| :--- | :--- | :--- | :--- |
| $\text{BASE\_URL}$ | $\text{[https://huggingface.co/rhasspy/piper-voices/resolve](https://huggingface.co/rhasspy/piper-voices/resolve)}$ | $\text{[https://huggingface.co/neurlang/piper-onnx-kss-korean/resolve](https://huggingface.co/neurlang/piper-onnx-kss-korean/resolve)}$ | 새로운 모델 저장소 $\text{URL}$로 변경합니다. |
| $\text{VOICE\_VERSION}$ | `v1.0.0` | `main` | $\text{Hugging Face}$에서 최신 파일을 다운받기 위해 브랜치 이름인 `main`을 사용합니다. |
| $\text{VOICE\_ID}$ | `ko_KR-kss_high` | `kss-korean` | 실제 $\text{ONNX}$ 및 $\text{JSON}$ 파일의 기본 이름입니다. |
| $\text{VOICE\_PATH\_DIR}$ | `ko/ko_KR/kss_high` | `main` | 파일들이 `main` 브랜치 바로 아래에 있으므로, 경로를 `main`으로 단순화합니다. |

**수정된 $\text{voices-fetcher}$ 환경 변수:**

```yaml
  # ======================= 자동 다운로드 서비스 (START) =======================
  voices-fetcher:
    # ... (생략) ...
    environment:
      VOICE_VERSION: "main" 
      VOICE_ID: "kss-korean" 
      BASE_URL: "https://huggingface.co/neurlang/piper-onnx-kss-korean/resolve"
      VOICE_PATH_DIR: "main"
    # ... (생략) ...
    command:
      - sh
      - -lc
      - |
        # ... (생략) ...
        
        # curl 명령: BASE_URL/VERSION/VOICE_PATH_DIR/VOICE_ID.onnx?download=true 형식 사용
        # VOICE_VERSION과 VOICE_PATH_DIR이 모두 'main'으로 설정되어, URL은 /main/main/kss-korean.onnx가 됩니다.
        # kss-korean 모델은 보통 파일이 루트에 있으므로, 명령어를 다음과 같이 수정합니다.
        
        # 경로를 /main/파일이름.onnx로 수정 (VOICE_PATH_DIR을 사용하지 않음)
        curl -fL -o "$$VOICE_ID.onnx" "$$BASE_URL/$$VOICE_VERSION/$$VOICE_ID.onnx?download=true"
        curl -fL -o "$$VOICE_ID.onnx.json" "$$BASE_URL/$$VOICE_VERSION/$$VOICE_ID.onnx.json?download=true"
        
        echo "[voices-fetcher] done"
    restart: "no"
  # ======================= 자동 다운로드 서비스 (END) =========================
```

-----

## 3\. $\text{Piper}$ $\text{CLI}$ 테스트 (컨테이너 내부)

$\text{Docker Compose}$로 서비스들을 구동하고, $\text{tts-server}$ 컨테이너($\text{Piper}$ $\text{CLI}$가 설치된 곳)가 시작된 후, $\text{Piper}$ $\text{CLI}$를 사용하여 음성 합성을 수동으로 테스트해 볼 수 있습니다.

### 🔹 테스트 단계

1.  **$\text{Docker Compose}$ 실행:**
    $\text{Dockerfile}$과 $\text{docker-compose.yml}$을 수정한 후 빌드 및 실행합니다.

    ```bash
    docker compose -f compose.fixed2.yml up --build -d
    ```

2.  **$\text{tts-server}$ 컨테이너 접근:**

    ```bash
    docker exec -it <tts-server-컨테이너-ID> /bin/bash
    ```

    > `<tts-server-컨테이너-ID>`는 `docker ps` 명령으로 확인 가능하며, 보통 `docker-tts-server-1`과 같은 이름일 것입니다.

3.  **$\text{Piper}$ $\text{CLI}$로 음성 합성 테스트:**
    다운로드한 모델 파일은 `/data/local/voices/kss-korean` 경로에 있습니다. $\text{Piper}$ 명령어로 텍스트를 음성으로 변환합니다.

    ```bash
    # 컨테이너 내부에서 실행

    # 다운로드된 모델 경로 설정 (voices-fetcher 서비스의 VOICE_ID를 따름)
    MODEL_DIR="/data/local/voices/kss-korean"

    /usr/local/bin/piper \
        --model "$MODEL_DIR/kss-korean.onnx" \
        --config "$MODEL_DIR/kss-korean.onnx.json" \
        --output_file "test_korean.wav" \
        --text "사용자 앱 개발을 환영합니다. 파이퍼 음성 합성이 성공적으로 완료되었습니다."
    ```

4.  **결과 확인:**
    명령이 성공적으로 실행되면, 컨테이너 내부에 `test_korean.wav` 파일이 생성됩니다. 이 파일을 호스트로 복사하여 음성을 확인하거나, $\text{tts-server}$ 앱의 API로 변환을 시도할 수 있습니다.