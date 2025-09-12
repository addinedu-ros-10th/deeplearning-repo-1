"""
스케줄 작업 모델
비삭제 정책을 적용한 모델 정의
"""

from __future__ import annotations
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy import String, Boolean, TIMESTAMP, text, Index
import uuid
from datetime import datetime
from typing import Optional, Dict, Any

class Base(DeclarativeBase):
    """기본 모델 클래스"""
    pass

def gen_uuid() -> str:
    """UUID 생성 함수"""
    return str(uuid.uuid4())

class ScheduledJob(Base):
    """스케줄 작업 모델 - 비삭제 정책 적용"""
    __tablename__ = "scheduled_jobs"

    # 기본 필드
    id: Mapped[str] = mapped_column(
        String(36), 
        primary_key=True, 
        default=gen_uuid,
        comment="작업 고유 ID"
    )
    name: Mapped[str] = mapped_column(
        String(120), 
        unique=True, 
        index=True,
        comment="작업 이름"
    )
    func: Mapped[str] = mapped_column(
        String(200),
        comment="실행할 함수 (module:function 형태)"
    )
    cron: Mapped[str] = mapped_column(
        String(64),
        comment="Cron 표현식"
    )
    args: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, 
        default=dict,
        comment="함수 인자"
    )
    kwargs: Mapped[Dict[str, Any]] = mapped_column(
        JSONB, 
        default=dict,
        comment="함수 키워드 인자"
    )
    
    # 상태 관리
    enabled: Mapped[bool] = mapped_column(
        Boolean, 
        default=True,
        comment="작업 활성화 여부"
    )
    last_run_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), 
        nullable=True,
        comment="마지막 실행 시간"
    )
    next_run_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), 
        nullable=True,
        comment="다음 실행 시간"
    )
    status: Mapped[str] = mapped_column(
        String(32), 
        default="idle",
        comment="작업 상태 (idle, running, failed, completed)"
    )
    
    # 비삭제 정책을 위한 필드
    is_deleted: Mapped[bool] = mapped_column(
        Boolean, 
        default=False,
        comment="논리 삭제 여부"
    )
    deleted_at: Mapped[Optional[datetime]] = mapped_column(
        TIMESTAMP(timezone=True), 
        nullable=True,
        comment="논리 삭제 시간"
    )
    
    # 메타데이터
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        server_default=text("now()"),
        comment="생성 시간"
    )
    updated_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), 
        server_default=text("now()"),
        onupdate=text("now()"),
        comment="수정 시간"
    )
    
    # 인덱스 정의
    __table_args__ = (
        Index('ix_scheduled_jobs_name', 'name', unique=True),
        Index('ix_scheduled_jobs_enabled', 'enabled'),
        Index('ix_scheduled_jobs_status', 'status'),
        Index('ix_scheduled_jobs_is_deleted', 'is_deleted'),
        Index('ix_scheduled_jobs_next_run', 'next_run_at'),
    )
    
    def soft_delete(self):
        """논리 삭제 수행"""
        self.is_deleted = True
        self.deleted_at = datetime.utcnow()
        self.enabled = False
    
    def restore(self):
        """논리 삭제 복원"""
        self.is_deleted = False
        self.deleted_at = None
    
    def __repr__(self) -> str:
        return f"<ScheduledJob(id='{self.id}', name='{self.name}', enabled={self.enabled})>"
