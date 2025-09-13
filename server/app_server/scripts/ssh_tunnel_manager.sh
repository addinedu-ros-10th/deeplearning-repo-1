#!/bin/bash

# SSH 터널 관리 스크립트
# Docker Compose 시작 전에 SSH 터널 상태를 확인하고 필요시 생성

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
SSH_TUNNEL_PORT=15432
SSH_KEY_PATH="secret/iot_db_key_pair.pem"
SSH_USER="ubuntu"
SSH_HOST="ec2-52-79-78-247.ap-northeast-2.compute.amazonaws.com"
SSH_REMOTE_PORT=5432
DB_HOST="localhost"
DB_PORT=15432
DB_USER="svc_dev"
DB_PASSWORD="IOT_dev_123!@#"
DB_NAME="iot_care"

# SSH 터널 PID 파일
SSH_PID_FILE="/tmp/ssh_tunnel_${SSH_TUNNEL_PORT}.pid"

# 포트 사용 여부 확인
check_port_usage() {
    if lsof -i :${SSH_TUNNEL_PORT} >/dev/null 2>&1; then
        return 0  # 포트 사용 중
    else
        return 1  # 포트 사용 안함
    fi
}

# SSH 터널 프로세스 확인
check_ssh_tunnel() {
    # PID 파일로 확인
    if [ -f "$SSH_PID_FILE" ]; then
        local pid=$(cat "$SSH_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            return 0  # SSH 터널 실행 중
        else
            rm -f "$SSH_PID_FILE"
            return 1  # SSH 터널 종료됨
        fi
    fi
    
    # PID 파일이 없어도 SSH 프로세스가 포트를 사용하고 있는지 확인
    local ssh_pids=$(lsof -ti :${SSH_TUNNEL_PORT} 2>/dev/null | xargs ps -p 2>/dev/null | grep ssh | awk '{print $1}')
    if [ -n "$ssh_pids" ]; then
        # SSH 프로세스가 실행 중이면 PID 파일 생성
        echo "$ssh_pids" | head -1 > "$SSH_PID_FILE"
        return 0
    fi
    
    return 1  # SSH 터널 없음
}

# SSH 키 파일 확인
check_ssh_key() {
    if [ ! -f "$SSH_KEY_PATH" ]; then
        log_error "SSH 키 파일을 찾을 수 없습니다: $SSH_KEY_PATH"
        return 1
    fi
    
    if [ ! -r "$SSH_KEY_PATH" ]; then
        log_error "SSH 키 파일에 읽기 권한이 없습니다: $SSH_KEY_PATH"
        return 1
    fi
    
    return 0
}

# SSH 터널 생성
create_ssh_tunnel() {
    log_info "SSH 터널을 생성합니다..."
    
    # 기존 SSH 터널 종료
    if check_ssh_tunnel; then
        log_info "기존 SSH 터널을 종료합니다..."
        kill_ssh_tunnel
    fi
    
    # SSH 키 파일 확인
    if ! check_ssh_key; then
        return 1
    fi
    
    # SSH 터널 생성
    ssh -i "$SSH_KEY_PATH" \
        -L 0.0.0.0:${SSH_TUNNEL_PORT}:localhost:${SSH_REMOTE_PORT} \
        -N -f \
        -o StrictHostKeyChecking=no \
        -o UserKnownHostsFile=/dev/null \
        -o ServerAliveInterval=60 \
        -o ServerAliveCountMax=3 \
        "${SSH_USER}@${SSH_HOST}" &
    
    local ssh_pid=$!
    echo $ssh_pid > "$SSH_PID_FILE"
    
    # SSH 터널 생성 대기
    sleep 3
    
    if check_ssh_tunnel; then
        log_success "SSH 터널이 성공적으로 생성되었습니다 (PID: $ssh_pid)"
        return 0
    else
        log_error "SSH 터널 생성에 실패했습니다"
        return 1
    fi
}

# SSH 터널 종료
kill_ssh_tunnel() {
    if [ -f "$SSH_PID_FILE" ]; then
        local pid=$(cat "$SSH_PID_FILE")
        if ps -p "$pid" > /dev/null 2>&1; then
            log_info "SSH 터널을 종료합니다 (PID: $pid)..."
            kill $pid
            sleep 2
            if ps -p "$pid" > /dev/null 2>&1; then
                log_warning "SSH 터널이 정상적으로 종료되지 않아 강제 종료합니다..."
                kill -9 $pid
            fi
        fi
        rm -f "$SSH_PID_FILE"
        log_success "SSH 터널이 종료되었습니다"
    fi
}

# 데이터베이스 연결 테스트
test_db_connection() {
    log_info "데이터베이스 연결을 테스트합니다..."
    
    # Python을 사용한 연결 테스트 (더 안정적)
    if test_db_connection_python; then
        log_success "데이터베이스 연결이 성공했습니다"
        return 0
    else
        log_error "데이터베이스 연결에 실패했습니다"
        return 1
    fi
}

# Python을 사용한 데이터베이스 연결 테스트
test_db_connection_python() {
    python3 -c "
import asyncpg
import asyncio
import sys

async def test_connection():
    try:
        conn = await asyncpg.connect(
            host='$DB_HOST',
            port=$DB_PORT,
            user='$DB_USER',
            password='$DB_PASSWORD',
            database='$DB_NAME'
        )
        result = await conn.fetchval('SELECT 1')
        await conn.close()
        print('데이터베이스 연결 성공')
        return True
    except Exception as e:
        print(f'데이터베이스 연결 실패: {e}')
        return False

if asyncio.run(test_connection()):
    sys.exit(0)
else:
    sys.exit(1)
" 2>&1
}

# 포트 사용 프로세스 정보 확인
get_port_process_info() {
    local port=$1
    local process_info=$(lsof -i :${port} 2>/dev/null | tail -n +2)
    
    if [ -n "$process_info" ]; then
        echo "$process_info"
        return 0
    else
        return 1
    fi
}

# SSH 터널 연결 테스트
test_ssh_tunnel_connection() {
    log_info "SSH 터널 연결을 테스트합니다..."
    
    # SSH 터널이 실제로 작동하는지 확인
    if nc -z localhost ${SSH_TUNNEL_PORT} 2>/dev/null; then
        log_success "SSH 터널 포트 ${SSH_TUNNEL_PORT}이 응답합니다"
        return 0
    else
        log_warning "SSH 터널 포트 ${SSH_TUNNEL_PORT}이 응답하지 않습니다"
        return 1
    fi
}

# 포트 사용 프로세스 진단
diagnose_port_usage() {
    local port=$1
    log_info "포트 ${port} 사용 프로세스를 진단합니다..."
    
    local process_info=$(get_port_process_info $port)
    if [ -n "$process_info" ]; then
        log_info "포트 ${port}을 사용하는 프로세스:"
        echo "$process_info"
        
        # SSH 터널 프로세스인지 확인
        if echo "$process_info" | grep -q "ssh"; then
            log_info "SSH 프로세스가 포트를 사용하고 있습니다"
            return 0
        else
            log_warning "SSH가 아닌 다른 프로세스가 포트를 사용하고 있습니다"
            return 1
        fi
    else
        log_info "포트 ${port}을 사용하는 프로세스를 찾을 수 없습니다"
        return 1
    fi
}

# 포트 정리 (SSH 터널만)
cleanup_ssh_tunnel() {
    log_info "SSH 터널을 정리합니다..."
    
    if check_ssh_tunnel; then
        local pid=$(cat "$SSH_PID_FILE")
        log_info "SSH 터널 프로세스를 종료합니다 (PID: $pid)..."
        kill $pid
        sleep 2
        
        if ps -p "$pid" > /dev/null 2>&1; then
            log_warning "SSH 터널이 정상적으로 종료되지 않아 강제 종료합니다..."
            kill -9 $pid
        fi
        
        rm -f "$SSH_PID_FILE"
        log_success "SSH 터널이 종료되었습니다"
    else
        log_info "실행 중인 SSH 터널이 없습니다"
    fi
}

# 포트 정리 (모든 프로세스)
cleanup_all_port_processes() {
    local port=$1
    log_warning "포트 ${port}을 사용하는 모든 프로세스를 정리합니다..."
    
    local pids=$(lsof -ti :${port} 2>/dev/null)
    if [ -n "$pids" ]; then
        for pid in $pids; do
            log_info "프로세스 ${pid}를 종료합니다..."
            kill $pid
            sleep 1
            if ps -p "$pid" > /dev/null 2>&1; then
                log_warning "프로세스 ${pid}가 정상적으로 종료되지 않아 강제 종료합니다..."
                kill -9 $pid
            fi
        done
        log_success "포트 ${port}을 사용하는 모든 프로세스가 종료되었습니다"
    else
        log_info "포트 ${port}을 사용하는 프로세스가 없습니다"
    fi
}

# 데이터베이스 연결 진단
diagnose_db_connection() {
    log_info "데이터베이스 연결을 진단합니다..."
    
    # 1. 포트 연결 테스트
    if ! test_ssh_tunnel_connection; then
        log_error "SSH 터널 포트 연결 실패"
        return 1
    fi
    
    # 2. 데이터베이스 연결 테스트
    if ! test_db_connection; then
        log_error "데이터베이스 연결 실패"
        
        # 3. 연결 정보 확인
        log_info "데이터베이스 연결 정보를 확인합니다..."
        log_info "호스트: ${DB_HOST}"
        log_info "포트: ${DB_PORT}"
        log_info "사용자: ${DB_USER}"
        log_info "데이터베이스: ${DB_NAME}"
        
        # 4. 네트워크 연결 테스트
        if nc -z ${DB_HOST} ${DB_PORT} 2>/dev/null; then
            log_info "네트워크 연결은 정상입니다"
            log_error "데이터베이스 인증 정보를 확인해주세요"
        else
            log_error "네트워크 연결에 실패했습니다"
        fi
        
        return 1
    fi
    
    return 0
}

# 메인 함수
main() {
    log_info "SSH 터널 관리 스크립트를 시작합니다..."
    
    # 포트 사용 여부 확인
    if check_port_usage; then
        log_info "포트 ${SSH_TUNNEL_PORT}이 사용 중입니다"
        
        # 포트 사용 프로세스 진단
        if diagnose_port_usage ${SSH_TUNNEL_PORT}; then
            log_info "SSH 프로세스가 포트를 사용하고 있습니다"
            
            # SSH 터널 프로세스 확인
            if check_ssh_tunnel; then
                log_success "SSH 터널이 이미 실행 중입니다"
                
                # 데이터베이스 연결 테스트
                if diagnose_db_connection; then
                    log_success "SSH 터널과 데이터베이스 연결이 정상입니다"
                    exit 0
                else
                    log_error "SSH 터널은 실행 중이지만 데이터베이스 연결에 실패했습니다"
                    log_info "SSH 터널을 재시작합니다..."
                    
                    cleanup_ssh_tunnel
                    if create_ssh_tunnel; then
                        if diagnose_db_connection; then
                            log_success "SSH 터널 재시작 후 데이터베이스 연결이 성공했습니다"
                            exit 0
                        else
                            log_error "SSH 터널 재시작 후에도 데이터베이스 연결에 실패했습니다"
                            exit 1
                        fi
                    else
                        log_error "SSH 터널 재시작에 실패했습니다"
                        exit 1
                    fi
                fi
            else
                log_warning "SSH 프로세스가 실행 중이지만 PID 파일을 찾을 수 없습니다"
                log_info "SSH 터널을 새로 생성합니다..."
                
                if create_ssh_tunnel; then
                    if diagnose_db_connection; then
                        log_success "SSH 터널 생성 후 데이터베이스 연결이 성공했습니다"
                        exit 0
                    else
                        log_error "SSH 터널 생성 후 데이터베이스 연결에 실패했습니다"
                        exit 1
                    fi
                else
                    log_error "SSH 터널 생성에 실패했습니다"
                    exit 1
                fi
            fi
        else
            log_warning "SSH가 아닌 다른 프로세스가 포트를 사용하고 있습니다"
            log_info "포트를 정리하고 SSH 터널을 생성합니다..."
            
            cleanup_all_port_processes ${SSH_TUNNEL_PORT}
            sleep 2
            
            if create_ssh_tunnel; then
                if diagnose_db_connection; then
                    log_success "포트 정리 후 SSH 터널 생성 및 데이터베이스 연결이 성공했습니다"
                    exit 0
                else
                    log_error "포트 정리 후에도 데이터베이스 연결에 실패했습니다"
                    exit 1
                fi
            else
                log_error "포트 정리 후 SSH 터널 생성에 실패했습니다"
                exit 1
            fi
        fi
    else
        log_info "포트 ${SSH_TUNNEL_PORT}이 사용되지 않습니다"
        log_info "SSH 터널을 생성합니다..."
        
        if create_ssh_tunnel; then
            if diagnose_db_connection; then
                log_success "SSH 터널 생성 및 데이터베이스 연결이 성공했습니다"
                exit 0
            else
                log_error "SSH 터널 생성 후 데이터베이스 연결에 실패했습니다"
                exit 1
            fi
        else
            log_error "SSH 터널 생성에 실패했습니다"
            exit 1
        fi
    fi
}

# 스크립트 종료 시 정리
cleanup() {
    log_info "스크립트를 종료합니다..."
    # 필요시 SSH 터널 종료 로직 추가
}

# 시그널 핸들러 설정
trap cleanup EXIT INT TERM

# 스크립트 실행
main "$@"
