"""
스케줄 작업 리포지토리
비삭제 정책을 적용한 CRUD 작업
"""

from typing import List, Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete, and_, or_
from sqlalchemy.orm import selectinload
from datetime import datetime
import logging

from ..models.scheduled_job import ScheduledJob

logger = logging.getLogger(__name__)

class ScheduledJobRepository:
    """스케줄 작업 리포지토리 - 비삭제 정책 적용"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, job_data: Dict[str, Any]) -> ScheduledJob:
        """새 스케줄 작업 생성"""
        try:
            job = ScheduledJob(**job_data)
            self.session.add(job)
            await self.session.commit()
            await self.session.refresh(job)
            logger.info(f"스케줄 작업 생성 완료: {job.name}")
            return job
        except Exception as e:
            await self.session.rollback()
            logger.error(f"스케줄 작업 생성 실패: {e}")
            raise
    
    async def get_by_id(self, job_id: str, include_deleted: bool = False) -> Optional[ScheduledJob]:
        """ID로 스케줄 작업 조회"""
        query = select(ScheduledJob).where(ScheduledJob.id == job_id)
        
        if not include_deleted:
            query = query.where(ScheduledJob.is_deleted == False)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_by_name(self, name: str, include_deleted: bool = False) -> Optional[ScheduledJob]:
        """이름으로 스케줄 작업 조회"""
        query = select(ScheduledJob).where(ScheduledJob.name == name)
        
        if not include_deleted:
            query = query.where(ScheduledJob.is_deleted == False)
        
        result = await self.session.execute(query)
        return result.scalar_one_or_none()
    
    async def get_all(self, include_deleted: bool = False, enabled_only: bool = False) -> List[ScheduledJob]:
        """모든 스케줄 작업 조회"""
        query = select(ScheduledJob)
        
        conditions = []
        if not include_deleted:
            conditions.append(ScheduledJob.is_deleted == False)
        if enabled_only:
            conditions.append(ScheduledJob.enabled == True)
        
        if conditions:
            query = query.where(and_(*conditions))
        
        query = query.order_by(ScheduledJob.created_at.desc())
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def get_enabled_jobs(self) -> List[ScheduledJob]:
        """활성화된 스케줄 작업만 조회"""
        query = select(ScheduledJob).where(
            and_(
                ScheduledJob.enabled == True,
                ScheduledJob.is_deleted == False
            )
        ).order_by(ScheduledJob.next_run_at.asc())
        
        result = await self.session.execute(query)
        return result.scalars().all()
    
    async def update(self, job_id: str, update_data: Dict[str, Any]) -> Optional[ScheduledJob]:
        """스케줄 작업 수정"""
        try:
            # 비삭제된 작업만 수정 가능
            query = select(ScheduledJob).where(
                and_(
                    ScheduledJob.id == job_id,
                    ScheduledJob.is_deleted == False
                )
            )
            result = await self.session.execute(query)
            job = result.scalar_one_or_none()
            
            if not job:
                logger.warning(f"수정할 스케줄 작업을 찾을 수 없습니다: {job_id}")
                return None
            
            # 업데이트할 필드만 수정
            for key, value in update_data.items():
                if hasattr(job, key) and key not in ['id', 'created_at', 'deleted_at']:
                    setattr(job, key, value)
            
            job.updated_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(job)
            
            logger.info(f"스케줄 작업 수정 완료: {job.name}")
            return job
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"스케줄 작업 수정 실패: {e}")
            raise
    
    async def soft_delete(self, job_id: str) -> bool:
        """스케줄 작업 논리 삭제"""
        try:
            query = select(ScheduledJob).where(
                and_(
                    ScheduledJob.id == job_id,
                    ScheduledJob.is_deleted == False
                )
            )
            result = await self.session.execute(query)
            job = result.scalar_one_or_none()
            
            if not job:
                logger.warning(f"삭제할 스케줄 작업을 찾을 수 없습니다: {job_id}")
                return False
            
            job.soft_delete()
            await self.session.commit()
            
            logger.info(f"스케줄 작업 논리 삭제 완료: {job.name}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"스케줄 작업 논리 삭제 실패: {e}")
            raise
    
    async def restore(self, job_id: str) -> bool:
        """스케줄 작업 복원"""
        try:
            query = select(ScheduledJob).where(
                and_(
                    ScheduledJob.id == job_id,
                    ScheduledJob.is_deleted == True
                )
            )
            result = await self.session.execute(query)
            job = result.scalar_one_or_none()
            
            if not job:
                logger.warning(f"복원할 스케줄 작업을 찾을 수 없습니다: {job_id}")
                return False
            
            job.restore()
            await self.session.commit()
            
            logger.info(f"스케줄 작업 복원 완료: {job.name}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"스케줄 작업 복원 실패: {e}")
            raise
    
    async def toggle_enabled(self, job_id: str) -> Optional[ScheduledJob]:
        """스케줄 작업 활성화/비활성화 토글"""
        try:
            query = select(ScheduledJob).where(
                and_(
                    ScheduledJob.id == job_id,
                    ScheduledJob.is_deleted == False
                )
            )
            result = await self.session.execute(query)
            job = result.scalar_one_or_none()
            
            if not job:
                logger.warning(f"토글할 스케줄 작업을 찾을 수 없습니다: {job_id}")
                return None
            
            job.enabled = not job.enabled
            job.updated_at = datetime.utcnow()
            await self.session.commit()
            await self.session.refresh(job)
            
            logger.info(f"스케줄 작업 토글 완료: {job.name} -> enabled={job.enabled}")
            return job
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"스케줄 작업 토글 실패: {e}")
            raise
    
    async def update_run_status(self, job_id: str, status: str, last_run_at: Optional[datetime] = None, next_run_at: Optional[datetime] = None) -> bool:
        """스케줄 작업 실행 상태 업데이트"""
        try:
            query = select(ScheduledJob).where(
                and_(
                    ScheduledJob.id == job_id,
                    ScheduledJob.is_deleted == False
                )
            )
            result = await self.session.execute(query)
            job = result.scalar_one_or_none()
            
            if not job:
                logger.warning(f"상태 업데이트할 스케줄 작업을 찾을 수 없습니다: {job_id}")
                return False
            
            job.status = status
            if last_run_at:
                job.last_run_at = last_run_at
            if next_run_at:
                job.next_run_at = next_run_at
            
            job.updated_at = datetime.utcnow()
            await self.session.commit()
            
            logger.debug(f"스케줄 작업 상태 업데이트 완료: {job.name} -> {status}")
            return True
            
        except Exception as e:
            await self.session.rollback()
            logger.error(f"스케줄 작업 상태 업데이트 실패: {e}")
            raise
    
    async def count(self, include_deleted: bool = False) -> int:
        """스케줄 작업 개수 조회"""
        query = select(ScheduledJob)
        
        if not include_deleted:
            query = query.where(ScheduledJob.is_deleted == False)
        
        result = await self.session.execute(query)
        return len(result.scalars().all())
    
    # 물리 삭제는 금지 (비삭제 정책)
    async def hard_delete(self, job_id: str) -> None:
        """물리 삭제 금지 - 비삭제 정책에 따라 예외 발생"""
        raise NotImplementedError("비삭제 정책에 따라 물리 삭제는 금지됩니다. soft_delete()를 사용하세요.")
