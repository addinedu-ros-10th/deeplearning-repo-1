FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# SSH 클라이언트 설치
RUN apt-get update && apt-get install -y \
    openssh-client \
    net-tools \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치 (최소한)
COPY pyproject.toml .
RUN pip install --upgrade pip && \
    pip install python-dotenv

# 스크립트 복사
COPY scripts /app/scripts

# SSH 디렉터리 생성
RUN mkdir -p /root/.ssh && \
    chmod 700 /root/.ssh

# 포트 노출 (SSH 터널용)
EXPOSE 15432

# 헬스체크
HEALTHCHECK --interval=10s --timeout=5s --start-period=20s --retries=3 \
    CMD netstat -an | grep 15432 || exit 1

# 기본 명령어
CMD ["python", "/app/scripts/ssh_tunnel.py"]
