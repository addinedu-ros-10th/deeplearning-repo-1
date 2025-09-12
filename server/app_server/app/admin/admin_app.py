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
        # 데이터베이스 매니저 초기화
        import asyncio
        asyncio.create_task(db_manager.initialize())
        
        self.admin = Admin(
            app=None,  # FastAPI 앱은 나중에 설정
            engine=db_manager.app_async_engine,
            title="IoT Care 스케줄러 관리",
            logo_url="https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png",
            templates_dir="templates/admin",
            statics_dir="static/admin"
        )
        
        # 관리자 뷰 등록
        self.admin.add_view(ScheduledJobAdmin)
    
    def mount_to_app(self, app):
        """FastAPI 앱에 SQLAdmin 마운트"""
        if self.admin:
            self.admin.app = app
            self.admin.mount_to(app)
    
    def get_admin(self):
        """SQLAdmin 인스턴스 반환"""
        return self.admin


# 전역 인스턴스
admin_app = AdminApp()
