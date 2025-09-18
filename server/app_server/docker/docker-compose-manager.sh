#!/bin/bash

# Docker Compose 관리 스크립트
# 사용법: ./docker-compose-manager.sh [local|prod|stop|status|logs]

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# 스크립트 디렉터리로 이동
cd "$(dirname "$0")/.."

# 환경변수 파일 경로
ENV_LOCAL="./secret/.env.local"
ENV_PROD="./secret/.env.prod"

# Docker Compose 파일 경로
COMPOSE_BASE="docker/compose.base.yml"
COMPOSE_LOCAL="docker/compose.local.yml"
COMPOSE_PROD="docker/compose.prod.yml"

# 로그 함수
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# 환경변수 파일 존재 확인
check_env_file() {
    local env_file=$1
    if [ ! -f "$env_file" ]; then
        log_error "환경변수 파일이 존재하지 않습니다: $env_file"
        exit 1
    fi
    log_info "환경변수 파일 확인: $env_file"
}

# Docker Compose 파일 존재 확인
check_compose_files() {
    local compose_files=("$COMPOSE_BASE" "$COMPOSE_LOCAL" "$COMPOSE_PROD")
    for file in "${compose_files[@]}"; do
        if [ ! -f "$file" ]; then
            log_error "Docker Compose 파일이 존재하지 않습니다: $file"
            exit 1
        fi
    done
    log_info "Docker Compose 파일 확인 완료"
}

# 로컬 환경 실행
start_local() {
    log_info "로컬 개발 환경을 시작합니다..."
    check_env_file "$ENV_LOCAL"
    check_compose_files
    
    log_info "Docker Compose 실행 중..."
    docker compose --env-file "$ENV_LOCAL" -f "$COMPOSE_BASE" -f "$COMPOSE_LOCAL" up -d --build
    
    if [ $? -eq 0 ]; then
        log_success "로컬 환경이 성공적으로 시작되었습니다!"
        log_info "API 서버: http://localhost:8000"
        log_info "관리자 패널: http://localhost:8000/admin"
        log_info "API 문서: http://localhost:8000/docs"
    else
        log_error "로컬 환경 시작에 실패했습니다."
        exit 1
    fi
}

# 운영 환경 실행
start_prod() {
    log_info "운영 환경을 시작합니다..."
    check_env_file "$ENV_PROD"
    check_compose_files
    
    log_warning "운영 환경을 시작합니다. 계속하시겠습니까? (y/N)"
    read -r response
    if [[ ! "$response" =~ ^[Yy]$ ]]; then
        log_info "운영 환경 시작이 취소되었습니다."
        exit 0
    fi
    
    log_info "Docker Compose 실행 중..."
    docker compose --env-file "$ENV_PROD" -f "$COMPOSE_BASE" -f "$COMPOSE_PROD" up -d --build
    
    if [ $? -eq 0 ]; then
        log_success "운영 환경이 성공적으로 시작되었습니다!"
        log_info "API 서버: http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com/"
        log_info "관리자 패널: http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com/admin"
        log_info "API 문서: http://ec2-43-201-96-23.ap-northeast-2.compute.amazonaws.com/docs"
    else
        log_error "운영 환경 시작에 실패했습니다."
        exit 1
    fi
}

# 모든 환경 중지
stop_all() {
    log_info "모든 Docker Compose 환경을 중지합니다..."
    
    # 로컬 환경 중지
    if [ -f "$ENV_LOCAL" ]; then
        log_info "로컬 환경 중지 중..."
        docker compose --env-file "$ENV_LOCAL" -f "$COMPOSE_BASE" -f "$COMPOSE_LOCAL" down 2>/dev/null || true
    fi
    
    # 운영 환경 중지
    if [ -f "$ENV_PROD" ]; then
        log_info "운영 환경 중지 중..."
        docker compose --env-file "$ENV_PROD" -f "$COMPOSE_BASE" -f "$COMPOSE_PROD" down 2>/dev/null || true
    fi
    
    log_success "모든 환경이 중지되었습니다."
}

# 상태 확인
show_status() {
    log_info "Docker Compose 상태를 확인합니다..."
    
    echo -e "\n${BLUE}=== 컨테이너 상태 ===${NC}"
    docker ps --format "table {{.Names}}\t{{.Status}}\t{{.Ports}}"
    
    echo -e "\n${BLUE}=== 네트워크 상태 ===${NC}"
    docker network ls | grep docker
    
    echo -e "\n${BLUE}=== 볼륨 상태 ===${NC}"
    docker volume ls | grep docker
}

# 로그 확인
show_logs() {
    local env=${1:-local}
    
    if [ "$env" = "local" ]; then
        check_env_file "$ENV_LOCAL"
        log_info "로컬 환경 로그를 확인합니다..."
        docker compose --env-file "$ENV_LOCAL" -f "$COMPOSE_BASE" -f "$COMPOSE_LOCAL" logs -f
    elif [ "$env" = "prod" ]; then
        check_env_file "$ENV_PROD"
        log_info "운영 환경 로그를 확인합니다..."
        docker compose --env-file "$ENV_PROD" -f "$COMPOSE_BASE" -f "$COMPOSE_PROD" logs -f
    else
        log_error "잘못된 환경입니다. local 또는 prod를 사용하세요."
        exit 1
    fi
}

# API 테스트
test_api() {
    log_info "API 서버를 테스트합니다..."
    
    # Health Check
    if curl -s http://localhost:8000/health > /dev/null; then
        log_success "API 서버가 정상적으로 응답합니다."
        
        # 루트 API 테스트
        echo -e "\n${BLUE}=== 루트 API 응답 ===${NC}"
        curl -s http://localhost:8000/ | jq . 2>/dev/null || curl -s http://localhost:8000/
        
        # ML Registry API 테스트
        echo -e "\n${BLUE}=== ML Registry API 응답 ===${NC}"
        curl -s http://localhost:8000/api/v1/datasets/ | jq . 2>/dev/null || curl -s http://localhost:8000/api/v1/datasets/
        
    else
        log_error "API 서버에 연결할 수 없습니다."
        exit 1
    fi
}

# 도움말 표시
show_help() {
    echo -e "${BLUE}Docker Compose 관리 스크립트${NC}"
    echo ""
    echo "사용법: $0 [COMMAND]"
    echo ""
    echo "명령어:"
    echo "  local     로컬 개발 환경 시작"
    echo "  prod      운영 환경 시작"
    echo "  stop      모든 환경 중지"
    echo "  status    컨테이너 상태 확인"
    echo "  logs      로그 확인 (local|prod)"
    echo "  test      API 서버 테스트"
    echo "  help      도움말 표시"
    echo ""
    echo "예시:"
    echo "  $0 local          # 로컬 환경 시작"
    echo "  $0 prod           # 운영 환경 시작"
    echo "  $0 stop           # 모든 환경 중지"
    echo "  $0 status         # 상태 확인"
    echo "  $0 logs local     # 로컬 환경 로그"
    echo "  $0 test           # API 테스트"
}

# 메인 로직
case "${1:-help}" in
    local)
        start_local
        ;;
    prod)
        start_prod
        ;;
    stop)
        stop_all
        ;;
    status)
        show_status
        ;;
    logs)
        show_logs "$2"
        ;;
    test)
        test_api
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        log_error "알 수 없는 명령어입니다: $1"
        show_help
        exit 1
        ;;
esac

