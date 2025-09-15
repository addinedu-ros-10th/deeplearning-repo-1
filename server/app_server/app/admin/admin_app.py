"""
SQLAdmin 메인 애플리케이션 설정
"""

from sqladmin import Admin, BaseView
from fastapi import Request
from app.infrastructure.db.session import db_manager
from app.admin.scheduled_job_admin import ScheduledJobAdmin
import os
from dotenv import load_dotenv

# 환경 변수 로딩
load_dotenv('secret/.env.local')

class AdminApp:
    """SQLAdmin 애플리케이션 관리 클래스"""
    
    def __init__(self):
        self.admin = None
        self._setup_admin()
    
    def _setup_admin(self):
        """SQLAdmin 설정"""
        # 임시로 None으로 설정하고 나중에 초기화
        self.admin = None
    
    def mount_to_app(self, app):
        """FastAPI 앱에 SQLAdmin 마운트"""
        try:
            # 동기 엔진 사용 (SQLAdmin은 동기 엔진 필요)
            from app.infrastructure.db.session import get_sync_engine
            
            # 동기 엔진 생성
            engine = get_sync_engine()
            
            self.admin = Admin(
                app=app,
                engine=engine,
                title="IoT Care 스케줄러 관리",
                logo_url="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
            )
            
            # 관리자 뷰 등록
            self.admin.add_view(ScheduledJobAdmin)
            print("✅ SQLAdmin 초기화 성공")
            
        except Exception as e:
            print(f"⚠️ SQLAdmin 초기화 실패: {e}")
            self.admin = None
    
    def get_admin(self):
        """SQLAdmin 인스턴스 반환"""
        return self.admin


# 전역 인스턴스
admin_app = AdminApp()
