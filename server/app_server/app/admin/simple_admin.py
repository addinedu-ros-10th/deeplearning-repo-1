"""
간단한 SQLAdmin 설정 (동기 엔진 사용)
"""

from sqladmin import Admin
from sqlalchemy import create_engine
import os
from dotenv import load_dotenv

# 환경 변수 로딩
load_dotenv('secret/.env.local')

def create_admin_app(fastapi_app):
    """SQLAdmin 애플리케이션 생성"""
    
    # 데이터베이스 URL 설정 (동기 엔진용)
    db_url = 'postgresql://svc_dev:IOT_dev_123%21%40%23@0.0.0.0:15432/iot_care'
    
    # 동기 엔진 생성
    engine = create_engine(db_url)
    
    # SQLAdmin 생성
    admin = Admin(
        app=fastapi_app,
        engine=engine,
        title="IoT Care 스케줄러 관리"
    )
    
    return admin