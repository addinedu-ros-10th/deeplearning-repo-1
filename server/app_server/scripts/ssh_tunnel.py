#!/usr/bin/env python3
"""
SSH 터널 자동 생성 및 관리 스크립트
서버 기동 시 자동으로 SSH 터널을 생성하여 DB에 접속할 수 있도록 함
"""

import os
import sys
import time
import signal
import subprocess
import logging
from pathlib import Path
from typing import Optional

# 로깅 설정
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SSHTunnelManager:
    def __init__(self):
        self.tunnel_process: Optional[subprocess.Popen] = None
        self.is_running = False
        
    def start_tunnel(self) -> bool:
        """SSH 터널 시작"""
        try:
            # 환경 변수에서 SSH 터널 설정 읽기
            tunnel_enable = os.getenv('SSH_TUNNEL_ENABLE', 'false').lower() == 'true'
            if not tunnel_enable:
                logger.info("SSH 터널이 비활성화되어 있습니다.")
                return True
                
            local_port = os.getenv('SSH_TUNNEL_LOCAL_PORT', '15432')
            remote_host = os.getenv('SSH_TUNNEL_REMOTE_HOST')
            remote_port = os.getenv('SSH_TUNNEL_REMOTE_PORT', '5432')
            bastion_host = os.getenv('SSH_TUNNEL_BASTION_HOST')
            user = os.getenv('SSH_TUNNEL_USER', 'ubuntu')
            key_path = os.getenv('SSH_TUNNEL_KEY_PATH', '/app/secret/iot_db_key_pair.pem')
            
            if not all([remote_host, bastion_host, key_path]):
                logger.error("SSH 터널 설정이 불완전합니다.")
                return False
                
            # SSH 키 파일 권한 확인 및 설정
            key_file = Path(key_path)
            if not key_file.exists():
                logger.error(f"SSH 키 파일이 존재하지 않습니다: {key_path}")
                return False
                
            # SSH 키 파일 권한을 600으로 설정
            os.chmod(key_path, 0o600)
            
            # SSH 터널 명령어 구성 (0.0.0.0으로 바인딩하여 다른 프로그램에서도 접근 가능)
            ssh_command = [
                'ssh',
                '-N',  # 명령 실행하지 않음
                '-L', f'0.0.0.0:{local_port}:{remote_host}:{remote_port}',  # 0.0.0.0으로 바인딩
                '-i', key_path,  # SSH 키 파일
                '-o', 'StrictHostKeyChecking=no',  # 호스트 키 확인 비활성화
                '-o', 'UserKnownHostsFile=/dev/null',  # known_hosts 파일 사용 안함
                '-o', 'ServerAliveInterval=60',  # 연결 유지
                '-o', 'ServerAliveCountMax=3',  # 최대 재시도 횟수
                f'{user}@{bastion_host}'
            ]
            
            logger.info(f"SSH 터널 시작: 0.0.0.0:{local_port} -> {remote_host}:{remote_port}")
            logger.info(f"Bastion 호스트: {user}@{bastion_host}")
            logger.info(f"다른 프로그램에서 접근 가능: 0.0.0.0:{local_port}")
            
            # SSH 터널 프로세스 시작
            self.tunnel_process = subprocess.Popen(
                ssh_command,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                preexec_fn=os.setsid  # 새로운 세션 그룹 생성
            )
            
            # 터널이 정상적으로 시작되었는지 확인
            time.sleep(2)
            if self.tunnel_process.poll() is None:
                self.is_running = True
                logger.info("SSH 터널이 성공적으로 시작되었습니다.")
                return True
            else:
                stdout, stderr = self.tunnel_process.communicate()
                logger.error(f"SSH 터널 시작 실패: {stderr.decode()}")
                return False
                
        except Exception as e:
            logger.error(f"SSH 터널 시작 중 오류 발생: {e}")
            return False
    
    def stop_tunnel(self):
        """SSH 터널 중지"""
        if self.tunnel_process and self.is_running:
            try:
                # 프로세스 그룹 전체 종료
                os.killpg(os.getpgid(self.tunnel_process.pid), signal.SIGTERM)
                self.tunnel_process.wait(timeout=10)
                logger.info("SSH 터널이 중지되었습니다.")
            except subprocess.TimeoutExpired:
                # 강제 종료
                os.killpg(os.getpgid(self.tunnel_process.pid), signal.SIGKILL)
                logger.warning("SSH 터널을 강제로 중지했습니다.")
            except Exception as e:
                logger.error(f"SSH 터널 중지 중 오류 발생: {e}")
            finally:
                self.is_running = False
                self.tunnel_process = None
    
    def is_tunnel_healthy(self) -> bool:
        """SSH 터널 상태 확인"""
        if not self.tunnel_process or not self.is_running:
            return False
        return self.tunnel_process.poll() is None
    
    def wait_for_tunnel(self, timeout: int = 30) -> bool:
        """SSH 터널이 준비될 때까지 대기"""
        logger.info("SSH 터널 준비 대기 중...")
        
        for i in range(timeout):
            if self.is_tunnel_healthy():
                logger.info("SSH 터널이 준비되었습니다.")
                return True
            time.sleep(1)
            
        logger.error(f"SSH 터널 준비 시간 초과 ({timeout}초)")
        return False

def signal_handler(signum, frame):
    """시그널 핸들러"""
    logger.info(f"시그널 {signum} 수신, SSH 터널 중지 중...")
    tunnel_manager.stop_tunnel()
    sys.exit(0)

def main():
    """메인 함수"""
    global tunnel_manager
    tunnel_manager = SSHTunnelManager()
    
    # 시그널 핸들러 등록
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # SSH 터널 시작
    if not tunnel_manager.start_tunnel():
        logger.error("SSH 터널 시작 실패")
        sys.exit(1)
    
    # 터널이 준비될 때까지 대기
    if not tunnel_manager.wait_for_tunnel():
        logger.error("SSH 터널 준비 실패")
        tunnel_manager.stop_tunnel()
        sys.exit(1)
    
    logger.info("SSH 터널이 실행 중입니다. Ctrl+C로 중지할 수 있습니다.")
    
    try:
        # 터널이 실행되는 동안 대기
        while tunnel_manager.is_tunnel_healthy():
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("사용자에 의해 중지됨")
    finally:
        tunnel_manager.stop_tunnel()

if __name__ == "__main__":
    main()
