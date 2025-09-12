# Nginx Dockerfile for FastAPI Proxy

FROM nginx:1.27-alpine

# 필요한 패키지 설치
RUN apk add --no-cache curl wget

# Nginx 설정 파일 복사
COPY nginx/nginx.conf /etc/nginx/nginx.conf

# 정적 파일 디렉터리 생성
RUN mkdir -p /var/www/static

# 로그 디렉터리 생성
RUN mkdir -p /var/log/nginx

# 권한 설정
RUN chown -R nginx:nginx /var/www/static
RUN chown -R nginx:nginx /var/log/nginx

# 포트 노출
EXPOSE 80 443

# 헬스체크
HEALTHCHECK --interval=30s --timeout=10s --start-period=20s --retries=3 \
    CMD curl -f http://localhost/health || exit 1

# Nginx 실행
CMD ["nginx", "-g", "daemon off;"]
