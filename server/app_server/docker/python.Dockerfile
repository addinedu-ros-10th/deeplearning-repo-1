FROM python:3.12-slim

WORKDIR /app
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# 시스템 빌드 의존 (필요 최소)
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Python 의존성 설치
COPY pyproject.toml .
RUN pip install --upgrade pip && \
    pip install -e .

# 앱 코드 복사
COPY . /app

# Python path 설정
ENV PYTHONPATH=/app

# 디버깅: 파일 구조 확인
RUN ls -la /app && echo "---" && ls -la /app/app && echo "---" && find /app -name "*.py" | head -10

# 앱 디렉토리 권한 확인
RUN ls -la /app/app && echo "---" && cat /app/app/__init__.py

# 헬스체크용 curl 설치 확인
RUN curl --version

# 포트 노출
EXPOSE 8000

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# 기본 명령어
CMD ["uvicorn", "app.main:create_app", "--factory", "--host", "0.0.0.0", "--port", "8000"]
