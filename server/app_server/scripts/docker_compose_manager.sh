#!/bin/bash

# Docker Compose 관리 스크립트
# SSH 터널 확인 후 Docker Compose 실행

set -e

# 색상 정의
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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

# 설정 변수
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SSH_TUNNEL_SCRIPT="$SCRIPT_DIR/ssh_tunnel_manager.sh"
DOCKER_COMPOSE_FILES="-f docker/compose.base.yml -f docker/compose.local.yml"

# SSH 터널 스크립트 확인
check_ssh_tunnel_script() {
    if [ ! -f "$SSH_TUNNEL_SCRIPT" ]; then
        log_error "SSH 터널 스크립트를 찾을 수 없습니다: $SSH_TUNNEL_SCRIPT"
        return 1
    fi
    
    if [ ! -x "$SSH_TUNNEL_SCRIPT" ]; then
        log_error "SSH 터널 스크립트에 실행 권한이 없습니다: $SSH_TUNNEL_SCRIPT"
        return 1
    fi
    
    return 0
}

# SSH 터널 설정
setup_ssh_tunnel() {
    log_info "SSH 터널을 설정합니다..."
    
    if ! check_ssh_tunnel_script; then
        return 1
    fi
    
    # SSH 터널 스크립트 실행
    if "$SSH_TUNNEL_SCRIPT"; then
        log_success "SSH 터널 설정이 완료되었습니다"
        return 0
    else
        log_error "SSH 터널 설정에 실패했습니다"
        return 1
    fi
}

# Docker Compose 실행
run_docker_compose() {
    local action="$1"
    local additional_args="$2"
    
    log_info "Docker Compose를 실행합니다: $action"
    
    cd "$PROJECT_DIR"
    
    case "$action" in
        "up")
            docker-compose $DOCKER_COMPOSE_FILES up -d $additional_args
            ;;
        "down")
            docker-compose $DOCKER_COMPOSE_FILES down $additional_args
            ;;
        "restart")
            docker-compose $DOCKER_COMPOSE_FILES restart $additional_args
            ;;
        "logs")
            docker-compose $DOCKER_COMPOSE_FILES logs $additional_args
            ;;
        "ps")
            docker-compose $DOCKER_COMPOSE_FILES ps
            ;;
        *)
            log_error "알 수 없는 액션입니다: $action"
            return 1
            ;;
    esac
}

# 서비스 상태 확인
check_services() {
    log_info "서비스 상태를 확인합니다..."
    
    # Docker Compose 서비스 상태 확인
    if run_docker_compose "ps" >/dev/null 2>&1; then
        log_success "Docker Compose 서비스가 실행 중입니다"
        
        # API 서비스 헬스체크
        if curl -s http://localhost:8000/health >/dev/null 2>&1; then
            log_success "API 서비스가 정상 동작합니다"
        else
            log_warning "API 서비스에 접근할 수 없습니다"
        fi
        
        # Redis 서비스 확인
        if docker exec docker_redis_1 redis-cli ping >/dev/null 2>&1; then
            log_success "Redis 서비스가 정상 동작합니다"
        else
            log_warning "Redis 서비스에 접근할 수 없습니다"
        fi
        
    else
        log_warning "Docker Compose 서비스가 실행되지 않았습니다"
    fi
}

# 정리 함수
cleanup() {
    log_info "정리 작업을 수행합니다..."
    # 필요시 정리 로직 추가
}

# 도움말 출력
show_help() {
    echo "Docker Compose 관리 스크립트"
    echo ""
    echo "사용법: $0 [옵션] [액션]"
    echo ""
    echo "옵션:"
    echo "  -h, --help     이 도움말을 표시합니다"
    echo "  --no-ssh       SSH 터널 설정을 건너뜁니다"
    echo "  --check-only   서비스 상태만 확인합니다"
    echo ""
    echo "액션:"
    echo "  up            Docker Compose 서비스를 시작합니다"
    echo "  down          Docker Compose 서비스를 중지합니다"
    echo "  restart       Docker Compose 서비스를 재시작합니다"
    echo "  logs          Docker Compose 로그를 확인합니다"
    echo "  ps            Docker Compose 서비스 상태를 확인합니다"
    echo ""
    echo "예시:"
    echo "  $0 up                    # SSH 터널 설정 후 서비스 시작"
    echo "  $0 --no-ssh up          # SSH 터널 설정 없이 서비스 시작"
    echo "  $0 --check-only         # 서비스 상태만 확인"
    echo "  $0 down                 # 서비스 중지"
}

# 메인 함수
main() {
    local skip_ssh=false
    local check_only=false
    local action=""
    
    # 인수 파싱
    while [[ $# -gt 0 ]]; do
        case $1 in
            -h|--help)
                show_help
                exit 0
                ;;
            --no-ssh)
                skip_ssh=true
                shift
                ;;
            --check-only)
                check_only=true
                shift
                ;;
            up|down|restart|logs|ps)
                action="$1"
                shift
                ;;
            *)
                log_error "알 수 없는 옵션입니다: $1"
                show_help
                exit 1
                ;;
        esac
    done
    
    # 체크 전용 모드
    if [ "$check_only" = true ]; then
        check_services
        exit 0
    fi
    
    # 액션이 지정되지 않은 경우 기본값
    if [ -z "$action" ]; then
        action="up"
    fi
    
    log_info "Docker Compose 관리 스크립트를 시작합니다..."
    log_info "액션: $action"
    log_info "SSH 터널 건너뛰기: $skip_ssh"
    
    # SSH 터널 설정 (건너뛰기 옵션이 없는 경우)
    if [ "$skip_ssh" = false ] && [ "$action" = "up" ]; then
        if ! setup_ssh_tunnel; then
            log_error "SSH 터널 설정에 실패했습니다"
            exit 1
        fi
    fi
    
    # Docker Compose 실행
    if ! run_docker_compose "$action"; then
        log_error "Docker Compose 실행에 실패했습니다"
        exit 1
    fi
    
    # 서비스 상태 확인 (up 액션인 경우)
    if [ "$action" = "up" ]; then
        sleep 5  # 서비스 시작 대기
        check_services
    fi
    
    log_success "작업이 완료되었습니다"
}

# 시그널 핸들러 설정
trap cleanup EXIT INT TERM

# 스크립트 실행
main "$@"
