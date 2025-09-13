"""
Scheduled Job Use Cases

Contains the application business logic for scheduled job operations.
These use cases orchestrate domain objects and coordinate with ports.
"""

from __future__ import annotations
from typing import List, Optional
from datetime import datetime
from app.domain.entities.scheduled_job import ScheduledJob, JobStatus
from app.domain.value_objects.job_id import JobId
from app.domain.ports.scheduler_repository import SchedulerRepository
from app.domain.ports.scheduler_port import SchedulerPort
from app.domain.services.scheduler_domain_service import SchedulerDomainService
from app.application.dto.scheduled_job_dto import (
    CreateScheduledJobRequest,
    UpdateScheduledJobRequest,
    ScheduledJobResponse,
    ScheduledJobListResponse,
    SchedulerStatusResponse,
    JobExecutionResponse,
    SchedulerReloadResponse,
    JobExecutionResult
)


class CreateScheduledJobUseCase:
    """Use case for creating a new scheduled job"""
    
    def __init__(
        self,
        repository: SchedulerRepository,
        scheduler: SchedulerPort,
        domain_service: SchedulerDomainService
    ):
        self.repository = repository
        self.scheduler = scheduler
        self.domain_service = domain_service
    
    async def execute(self, request: CreateScheduledJobRequest) -> ScheduledJobResponse:
        """
        Create a new scheduled job
        
        Args:
            request: Create job request
            
        Returns:
            Created job response
            
        Raises:
            ValueError: If validation fails
            RepositoryError: If persistence fails
        """
        # Generate unique ID
        job_id = JobId.generate()
        
        # Create domain entity
        job = ScheduledJob(
            id=job_id.value,
            name=request.name,
            func=request.func,
            cron=request.cron,
            args=request.args,
            kwargs=request.kwargs,
            enabled=request.enabled,
            status=JobStatus.IDLE,
            last_run_at=None,
            next_run_at=None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Validate using domain service
        if not self.domain_service.validate_job_schedule(job):
            raise ValueError("Invalid job configuration")
        
        # Save to repository
        created_job = await self.repository.create(job)
        
        # Add to scheduler if enabled
        if created_job.enabled:
            await self.scheduler.add_job(
                job_id=job_id,
                func=created_job.func,
                trigger=created_job.cron,
                args=list(created_job.args.values()) if created_job.args else [],
                kwargs=created_job.kwargs
            )
        
        return ScheduledJobResponse.from_orm(created_job)


class GetScheduledJobUseCase:
    """Use case for getting a scheduled job by ID"""
    
    def __init__(self, repository: SchedulerRepository):
        self.repository = repository
    
    async def execute(self, job_id: str) -> Optional[ScheduledJobResponse]:
        """
        Get a scheduled job by ID
        
        Args:
            job_id: Job ID
            
        Returns:
            Job response or None if not found
        """
        job_id_obj = JobId.from_string(job_id)
        job = await self.repository.get_by_id(job_id_obj)
        
        if job is None:
            return None
        
        return ScheduledJobResponse.from_orm(job)


class ListScheduledJobsUseCase:
    """Use case for listing scheduled jobs"""
    
    def __init__(self, repository: SchedulerRepository):
        self.repository = repository
    
    async def execute(self, enabled_only: bool = False) -> ScheduledJobListResponse:
        """
        List scheduled jobs
        
        Args:
            enabled_only: If True, only return enabled jobs
            
        Returns:
            List of job responses
        """
        if enabled_only:
            jobs = await self.repository.get_enabled()
        else:
            jobs = await self.repository.get_all()
        
        job_responses = [ScheduledJobResponse.from_orm(job) for job in jobs]
        
        return ScheduledJobListResponse(
            jobs=job_responses,
            count=len(job_responses),
            timestamp=datetime.utcnow()
        )


class UpdateScheduledJobUseCase:
    """Use case for updating a scheduled job"""
    
    def __init__(
        self,
        repository: SchedulerRepository,
        scheduler: SchedulerPort,
        domain_service: SchedulerDomainService
    ):
        self.repository = repository
        self.scheduler = scheduler
        self.domain_service = domain_service
    
    async def execute(self, job_id: str, request: UpdateScheduledJobRequest) -> Optional[ScheduledJobResponse]:
        """
        Update a scheduled job
        
        Args:
            job_id: Job ID
            request: Update request
            
        Returns:
            Updated job response or None if not found
        """
        job_id_obj = JobId.from_string(job_id)
        existing_job = await self.repository.get_by_id(job_id_obj)
        
        if existing_job is None:
            return None
        
        # Update fields
        if request.name is not None:
            existing_job.name = request.name
        if request.func is not None:
            existing_job.update_function(request.func)
        if request.cron is not None:
            existing_job.update_schedule(request.cron)
        if request.args is not None:
            existing_job.args = request.args
        if request.kwargs is not None:
            existing_job.kwargs = request.kwargs
        if request.enabled is not None:
            if request.enabled:
                existing_job.enable()
            else:
                existing_job.disable()
        
        # Validate updated job
        if not self.domain_service.validate_job_schedule(existing_job):
            raise ValueError("Invalid job configuration after update")
        
        # Update in repository
        updated_job = await self.repository.update(existing_job)
        
        # Update in scheduler
        if updated_job.enabled:
            await self.scheduler.add_job(
                job_id=job_id_obj,
                func=updated_job.func,
                trigger=updated_job.cron,
                args=list(updated_job.args.values()) if updated_job.args else [],
                kwargs=updated_job.kwargs
            )
        else:
            await self.scheduler.remove_job(job_id_obj)
        
        return ScheduledJobResponse.from_orm(updated_job)


class DeleteScheduledJobUseCase:
    """Use case for deleting a scheduled job"""
    
    def __init__(self, repository: SchedulerRepository, scheduler: SchedulerPort):
        self.repository = repository
        self.scheduler = scheduler
    
    async def execute(self, job_id: str) -> bool:
        """
        Delete a scheduled job
        
        Args:
            job_id: Job ID
            
        Returns:
            True if deleted successfully, False if not found
        """
        job_id_obj = JobId.from_string(job_id)
        
        # Remove from scheduler first
        await self.scheduler.remove_job(job_id_obj)
        
        # Delete from repository
        return await self.repository.delete(job_id_obj)


class ExecuteScheduledJobUseCase:
    """Use case for executing a scheduled job immediately"""
    
    def __init__(self, scheduler: SchedulerPort):
        self.scheduler = scheduler
    
    async def execute(self, job_id: str) -> JobExecutionResponse:
        """
        Execute a scheduled job immediately
        
        Args:
            job_id: Job ID
            
        Returns:
            Execution response
        """
        job_id_obj = JobId.from_string(job_id)
        success = await self.scheduler.execute_job(job_id_obj)
        
        if success:
            return JobExecutionResponse(
                status="success",
                message=f"Job {job_id} executed successfully",
                timestamp=datetime.utcnow()
            )
        else:
            return JobExecutionResponse(
                status="failed",
                message=f"Failed to execute job {job_id}",
                timestamp=datetime.utcnow()
            )


class GetSchedulerStatusUseCase:
    """Use case for getting scheduler status"""
    
    def __init__(self, scheduler: SchedulerPort):
        self.scheduler = scheduler
    
    async def execute(self) -> SchedulerStatusResponse:
        """
        Get scheduler status
        
        Returns:
            Scheduler status response
        """
        status = await self.scheduler.get_scheduler_status()
        jobs = await self.scheduler.get_jobs()
        
        return SchedulerStatusResponse(
            scheduler_running=status.get('running', False),
            active_jobs=len(jobs),
            jobs=jobs,
            timestamp=datetime.utcnow()
        )


class ReloadSchedulerUseCase:
    """Use case for reloading scheduler jobs"""
    
    def __init__(
        self,
        repository: SchedulerRepository,
        scheduler: SchedulerPort,
        domain_service: SchedulerDomainService
    ):
        self.repository = repository
        self.scheduler = scheduler
        self.domain_service = domain_service
    
    async def execute(self) -> SchedulerReloadResponse:
        """
        Reload all jobs from repository into scheduler
        
        Returns:
            Reload response
        """
        try:
            # Get all enabled jobs from repository
            jobs = await self.repository.get_enabled()
            
            # Filter jobs that can be scheduled
            valid_jobs = [
                job for job in jobs 
                if self.domain_service.validate_job_schedule(job)
            ]
            
            # Reload jobs in scheduler
            jobs_reloaded = await self.scheduler.reload_jobs()
            
            return SchedulerReloadResponse(
                status="success",
                message="Scheduler reloaded successfully",
                jobs_reloaded=jobs_reloaded,
                timestamp=datetime.utcnow()
            )
            
        except Exception as e:
            return SchedulerReloadResponse(
                status="error",
                message=f"Failed to reload scheduler: {str(e)}",
                jobs_reloaded=0,
                timestamp=datetime.utcnow()
            )
