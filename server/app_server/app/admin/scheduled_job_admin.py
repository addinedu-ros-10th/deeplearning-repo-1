"""
ScheduledJob 모델을 위한 SQLAdmin 관리자 화면
"""

from sqladmin import ModelView
from app.infrastructure.db.models.scheduled_job import ScheduledJob
from datetime import datetime
from typing import Any, Dict, List, Optional


class ScheduledJobAdmin(ModelView, model=ScheduledJob):
    """스케줄 작업 관리자 화면"""
    
    # 기본 설정
    name = "스케줄 작업"
    name_plural = "스케줄 작업들"
    icon = "fa-solid fa-clock"
    
    # 표시할 컬럼 설정
    column_list = [
        "id",
        "name", 
        "func",
        "cron",
        "enabled",
        "status",
        "last_run_at",
        "next_run_at",
        "created_at"
    ]
    
    # 상세 보기에서 표시할 컬럼
    column_details_list = [
        "id",
        "name",
        "func", 
        "cron",
        "args",
        "kwargs",
        "enabled",
        "status",
        "last_run_at",
        "next_run_at",
        "created_at",
        "updated_at"
    ]
    
    # 검색 가능한 컬럼
    column_searchable_list = ["name", "func", "status"]
    
    # 필터링 가능한 컬럼
    column_filters = ["enabled", "status", "created_at"]
    
    # 정렬 가능한 컬럼
    column_sortable_list = ["name", "enabled", "status", "created_at", "last_run_at"]
    
    # 페이지네이션 설정
    page_size = 20
    page_size_options = [10, 20, 50, 100]
    
    # 폼 설정
    form_columns = [
        "name",
        "func", 
        "cron",
        "args",
        "kwargs",
        "enabled"
    ]
    
    # 읽기 전용 컬럼
    column_details_exclude_list = ["is_deleted", "deleted_at"]
    
    # 컬럼 레이블 설정
    column_labels = {
        "id": "ID",
        "name": "작업명",
        "func": "함수",
        "cron": "Cron 표현식",
        "args": "인수",
        "kwargs": "키워드 인수",
        "enabled": "활성화",
        "status": "상태",
        "last_run_at": "마지막 실행",
        "next_run_at": "다음 실행",
        "created_at": "생성일",
        "updated_at": "수정일"
    }
    
    # 컬럼 형식 설정
    column_formatters = {
        "created_at": lambda m, a: m.created_at.strftime("%Y-%m-%d %H:%M:%S") if m.created_at else "",
        "updated_at": lambda m, a: m.updated_at.strftime("%Y-%m-%d %H:%M:%S") if m.updated_at else "",
        "last_run_at": lambda m, a: m.last_run_at.strftime("%Y-%m-%d %H:%M:%S") if m.last_run_at else "실행 안됨",
        "next_run_at": lambda m, a: m.next_run_at.strftime("%Y-%m-%d %H:%M:%S") if m.next_run_at else "예정 없음"
    }
    
    # 상태별 색상 설정
    column_formatters_detail = {
        "status": lambda m, a: f'<span class="badge badge-{"success" if m.status == "idle" else "warning" if m.status == "running" else "danger"}">{m.status}</span>',
        "enabled": lambda m, a: f'<span class="badge badge-{"success" if m.enabled else "secondary"}">{"활성" if m.enabled else "비활성"}</span>'
    }
    
    # 검색 설정
    search_placeholder = "작업명, 함수명, 상태로 검색..."
    
    # 정렬 기본값
    column_default_sort = [("created_at", True)]
    
    # 삭제 정책 (논리 삭제만 허용)
    can_delete = False
    can_edit = True
    can_create = True
    can_view_details = True
    
    # 커스텀 액션
    def can_edit_model(self, model: Any) -> bool:
        """편집 권한 확인"""
        return True
    
    def can_create_model(self, model: Any) -> bool:
        """생성 권한 확인"""
        return True
    
    def can_view_details(self, model: Any) -> bool:
        """상세 보기 권한 확인"""
        return True
    
    # 폼 검증
    def validate_model(self, model: Any) -> bool:
        """모델 검증"""
        if not model.name:
            raise ValueError("작업명은 필수입니다.")
        if not model.func:
            raise ValueError("함수명은 필수입니다.")
        if not model.cron:
            raise ValueError("Cron 표현식은 필수입니다.")
        return True
    
    # 생성 전 처리
    def on_model_change(self, data: Dict[str, Any], model: Any, is_created: bool) -> None:
        """모델 변경 시 처리"""
        if is_created:
            model.created_at = datetime.utcnow()
        model.updated_at = datetime.utcnow()
        
        # 논리 삭제 정책 적용
        model.is_deleted = False
        model.deleted_at = None
