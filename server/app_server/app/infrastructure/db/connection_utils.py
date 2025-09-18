"""
데이터베이스 연결 유틸리티
환경변수 기반 DB 연결 파라미터 생성
"""

import os
import logging
from typing import Dict, Any, Optional
from urllib.parse import urlparse, unquote

logger = logging.getLogger(__name__)

def parse_db_url(db_url: str) -> Dict[str, Any]:
    """
    데이터베이스 URL을 파싱하여 asyncpg 연결 파라미터로 변환
    
    Args:
        db_url: 데이터베이스 연결 URL (postgresql:// 또는 postgresql+asyncpg://)
        
    Returns:
        asyncpg.connect()에 전달할 연결 파라미터 딕셔너리
    """
    try:
        # asyncpg 형식을 postgresql로 변환
        if db_url.startswith('postgresql+asyncpg://'):
            db_url = db_url.replace('postgresql+asyncpg://', 'postgresql://')
        
        # URL 파싱
        parsed = urlparse(db_url)
        
        # Docker 컨테이너에서 host.docker.internal 처리
        host = parsed.hostname or "localhost"
        if host == "host.docker.internal":
            host = "172.17.0.1"  # Docker 호스트의 실제 IP
        
        # 연결 파라미터 구성
        conn_params = {
            'host': host,
            'port': parsed.port or 5432,
            'user': unquote(parsed.username) if parsed.username else None,
            'password': unquote(parsed.password) if parsed.password else None,
            'database': parsed.path[1:] if parsed.path else None
        }
        
        # None 값 제거
        conn_params = {k: v for k, v in conn_params.items() if v is not None}
        
        logger.debug(f"DB 연결 파라미터: {conn_params}")
        return conn_params
        
    except Exception as e:
        logger.error(f"DB URL 파싱 실패: {e}")
        # 기본값 반환
        return {
            'host': '172.17.0.1',
            'port': 15432,
            'user': 'svc_dev',
            'password': 'IOT_dev_123!@#',
            'database': 'iot_care'
        }

def get_db_connection_params(env_var: str = 'DB_APP_URL') -> Dict[str, Any]:
    """
    환경변수에서 DB 연결 파라미터를 가져옴
    
    Args:
        env_var: 환경변수명 (기본값: 'DB_APP_URL')
        
    Returns:
        asyncpg.connect()에 전달할 연결 파라미터 딕셔너리
    """
    db_url = os.getenv(env_var)
    if not db_url:
        logger.warning(f"환경변수 {env_var}가 설정되지 않음. 기본값 사용")
        db_url = "postgresql://svc_dev:IOT_dev_123%21%40%23@host.docker.internal:15432/iot_care"
    
    return parse_db_url(db_url)

def get_ml_db_connection_params() -> Dict[str, Any]:
    """
    ML 스키마용 DB 연결 파라미터를 가져옴
    
    Returns:
        ML 스키마용 asyncpg 연결 파라미터 딕셔너리
    """
    # ML_DB_URL이 있으면 사용, 없으면 DB_APP_URL 사용
    ml_url = os.getenv('ML_DB_URL')
    if ml_url:
        return parse_db_url(ml_url)
    else:
        return get_db_connection_params('DB_APP_URL')

def get_legacy_db_connection_params() -> Dict[str, Any]:
    """
    레거시 스키마용 DB 연결 파라미터를 가져옴
    
    Returns:
        레거시 스키마용 asyncpg 연결 파라미터 딕셔너리
    """
    return get_db_connection_params('DB_LEGACY_URL')
