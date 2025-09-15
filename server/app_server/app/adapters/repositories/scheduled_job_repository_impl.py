"""
Scheduled Job Repository Implementation

SQLAlchemy implementation of the scheduler repository port.
This adapter implements the repository interface using SQLAlchemy.
"""

from __future__ import annotations
from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from sqlalchemy.orm import selectinload
from app.domain.entities.scheduled_job import ScheduledJob, JobStatus
from app.domain.value_objects.job_id import JobId
from app.domain.ports.scheduler_repository import SchedulerRepository
from app.infrastructure.db.models.scheduled_job import ScheduledJob as ScheduledJobModel


class ScheduledJobRepositoryImpl(SchedulerRepository):
    """
    SQLAlchemy implementation of the scheduler repository.
    
    This adapter implements the repository port using SQLAlchemy ORM.
    """
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def create(self, job: ScheduledJob) -> ScheduledJob:
        """Create a new scheduled job"""
        try:
            # Convert domain entity to ORM model
            job_model = ScheduledJobModel(
                id=job.id,
                name=job.name,
                func=job.func,
                cron=job.cron,
                args=job.args,
                kwargs=job.kwargs,
                enabled=job.enabled,
                status=job.status.value,
                last_run_at=job.last_run_at,
                next_run_at=job.next_run_at,
                created_at=job.created_at,
                updated_at=job.updated_at
            )
            
            self.session.add(job_model)
            await self.session.commit()
            await self.session.refresh(job_model)
            
            # Convert back to domain entity
            return self._model_to_entity(job_model)
            
        except Exception as e:
            await self.session.rollback()
            raise RepositoryError(f"Failed to create job: {str(e)}")
    
    async def get_by_id(self, job_id: JobId) -> Optional[ScheduledJob]:
        """Get a scheduled job by ID"""
        try:
            result = await self.session.execute(
                select(ScheduledJobModel).where(ScheduledJobModel.id == job_id.value)
            )
            job_model = result.scalar_one_or_none()
            
            if job_model is None:
                return None
            
            return self._model_to_entity(job_model)
            
        except Exception as e:
            raise RepositoryError(f"Failed to get job by ID: {str(e)}")
    
    async def get_by_name(self, name: str) -> Optional[ScheduledJob]:
        """Get a scheduled job by name"""
        try:
            result = await self.session.execute(
                select(ScheduledJobModel).where(ScheduledJobModel.name == name)
            )
            job_model = result.scalar_one_or_none()
            
            if job_model is None:
                return None
            
            return self._model_to_entity(job_model)
            
        except Exception as e:
            raise RepositoryError(f"Failed to get job by name: {str(e)}")
    
    async def get_all(self) -> List[ScheduledJob]:
        """Get all scheduled jobs"""
        try:
            result = await self.session.execute(
                select(ScheduledJobModel).order_by(ScheduledJobModel.created_at.desc())
            )
            job_models = result.scalars().all()
            
            return [self._model_to_entity(job_model) for job_model in job_models]
            
        except Exception as e:
            raise RepositoryError(f"Failed to get all jobs: {str(e)}")
    
    async def get_enabled(self) -> List[ScheduledJob]:
        """Get all enabled scheduled jobs"""
        try:
            result = await self.session.execute(
                select(ScheduledJobModel)
                .where(ScheduledJobModel.enabled == True)
                .order_by(ScheduledJobModel.created_at.desc())
            )
            job_models = result.scalars().all()
            
            return [self._model_to_entity(job_model) for job_model in job_models]
            
        except Exception as e:
            raise RepositoryError(f"Failed to get enabled jobs: {str(e)}")
    
    async def update(self, job: ScheduledJob) -> ScheduledJob:
        """Update an existing scheduled job"""
        try:
            # Update the model
            await self.session.execute(
                update(ScheduledJobModel)
                .where(ScheduledJobModel.id == job.id)
                .values(
                    name=job.name,
                    func=job.func,
                    cron=job.cron,
                    args=job.args,
                    kwargs=job.kwargs,
                    enabled=job.enabled,
                    status=job.status.value,
                    last_run_at=job.last_run_at,
                    next_run_at=job.next_run_at,
                    updated_at=job.updated_at
                )
            )
            
            await self.session.commit()
            
            # Get the updated model
            result = await self.session.execute(
                select(ScheduledJobModel).where(ScheduledJobModel.id == job.id)
            )
            updated_model = result.scalar_one()
            
            return self._model_to_entity(updated_model)
            
        except Exception as e:
            await self.session.rollback()
            raise RepositoryError(f"Failed to update job: {str(e)}")
    
    async def delete(self, job_id: JobId) -> bool:
        """Delete a scheduled job"""
        try:
            result = await self.session.execute(
                delete(ScheduledJobModel).where(ScheduledJobModel.id == job_id.value)
            )
            
            await self.session.commit()
            
            return result.rowcount > 0
            
        except Exception as e:
            await self.session.rollback()
            raise RepositoryError(f"Failed to delete job: {str(e)}")
    
    async def exists(self, job_id: JobId) -> bool:
        """Check if a scheduled job exists"""
        try:
            result = await self.session.execute(
                select(ScheduledJobModel.id).where(ScheduledJobModel.id == job_id.value)
            )
            return result.scalar_one_or_none() is not None
            
        except Exception as e:
            raise RepositoryError(f"Failed to check job existence: {str(e)}")
    
    async def count(self) -> int:
        """Get the total count of scheduled jobs"""
        try:
            result = await self.session.execute(
                select(ScheduledJobModel.id)
            )
            return len(result.scalars().all())
            
        except Exception as e:
            raise RepositoryError(f"Failed to count jobs: {str(e)}")
    
    def _model_to_entity(self, model: ScheduledJobModel) -> ScheduledJob:
        """Convert ORM model to domain entity"""
        return ScheduledJob(
            id=model.id,
            name=model.name,
            func=model.func,
            cron=model.cron,
            args=model.args or {},
            kwargs=model.kwargs or {},
            enabled=model.enabled,
            status=JobStatus(model.status),
            last_run_at=model.last_run_at,
            next_run_at=model.next_run_at,
            created_at=model.created_at,
            updated_at=model.updated_at
        )


class RepositoryError(Exception):
    """Repository operation error"""
    pass
