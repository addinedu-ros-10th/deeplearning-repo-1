"""
Scheduled Job HTTP Controller

HTTP adapter for scheduled job operations.
This controller handles HTTP requests and delegates to use cases.
"""

from __future__ import annotations
from typing import List
from fastapi import APIRouter, HTTPException, Depends
from app.application.use_cases.scheduled_job_use_cases import (
    CreateScheduledJobUseCase,
    GetScheduledJobUseCase,
    ListScheduledJobsUseCase,
    UpdateScheduledJobUseCase,
    DeleteScheduledJobUseCase,
    ExecuteScheduledJobUseCase,
    GetSchedulerStatusUseCase,
    ReloadSchedulerUseCase
)
from app.application.dto.scheduled_job_dto import (
    CreateScheduledJobRequest,
    UpdateScheduledJobRequest,
    ScheduledJobResponse,
    ScheduledJobListResponse,
    SchedulerStatusResponse,
    JobExecutionResponse,
    SchedulerReloadResponse
)


class ScheduledJobController:
    """HTTP controller for scheduled job operations"""
    
    def __init__(
        self,
        create_use_case: CreateScheduledJobUseCase,
        get_use_case: GetScheduledJobUseCase,
        list_use_case: ListScheduledJobsUseCase,
        update_use_case: UpdateScheduledJobUseCase,
        delete_use_case: DeleteScheduledJobUseCase,
        execute_use_case: ExecuteScheduledJobUseCase,
        status_use_case: GetSchedulerStatusUseCase,
        reload_use_case: ReloadSchedulerUseCase
    ):
        self.create_use_case = create_use_case
        self.get_use_case = get_use_case
        self.list_use_case = list_use_case
        self.update_use_case = update_use_case
        self.delete_use_case = delete_use_case
        self.execute_use_case = execute_use_case
        self.status_use_case = status_use_case
        self.reload_use_case = reload_use_case
        
        self.router = APIRouter(prefix="/api/v1/scheduled-jobs", tags=["scheduled-jobs"])
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup HTTP routes"""
        
        @self.router.post("/", response_model=ScheduledJobResponse)
        async def create_job(request: CreateScheduledJobRequest):
            """Create a new scheduled job"""
            try:
                return await self.create_use_case.execute(request)
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
        
        @self.router.get("/{job_id}", response_model=ScheduledJobResponse)
        async def get_job(job_id: str):
            """Get a scheduled job by ID"""
            job = await self.get_use_case.execute(job_id)
            if job is None:
                raise HTTPException(status_code=404, detail="Job not found")
            return job
        
        @self.router.get("/", response_model=ScheduledJobListResponse)
        async def list_jobs(enabled_only: bool = False):
            """List scheduled jobs"""
            return await self.list_use_case.execute(enabled_only)
        
        @self.router.put("/{job_id}", response_model=ScheduledJobResponse)
        async def update_job(job_id: str, request: UpdateScheduledJobRequest):
            """Update a scheduled job"""
            try:
                job = await self.update_use_case.execute(job_id, request)
                if job is None:
                    raise HTTPException(status_code=404, detail="Job not found")
                return job
            except ValueError as e:
                raise HTTPException(status_code=400, detail=str(e))
            except Exception as e:
                raise HTTPException(status_code=500, detail=f"Internal server error: {str(e)}")
        
        @self.router.delete("/{job_id}")
        async def delete_job(job_id: str):
            """Delete a scheduled job"""
            success = await self.delete_use_case.execute(job_id)
            if not success:
                raise HTTPException(status_code=404, detail="Job not found")
            return {"message": "Job deleted successfully"}
        
        @self.router.post("/{job_id}/execute", response_model=JobExecutionResponse)
        async def execute_job(job_id: str):
            """Execute a scheduled job immediately"""
            return await self.execute_use_case.execute(job_id)
        
        @self.router.get("/scheduler/status", response_model=SchedulerStatusResponse)
        async def get_scheduler_status():
            """Get scheduler status"""
            return await self.status_use_case.execute()
        
        @self.router.post("/scheduler/reload", response_model=SchedulerReloadResponse)
        async def reload_scheduler():
            """Reload scheduler jobs"""
            return await self.reload_use_case.execute()


def create_scheduled_job_router(
    create_use_case: CreateScheduledJobUseCase,
    get_use_case: GetScheduledJobUseCase,
    list_use_case: ListScheduledJobsUseCase,
    update_use_case: UpdateScheduledJobUseCase,
    delete_use_case: DeleteScheduledJobUseCase,
    execute_use_case: ExecuteScheduledJobUseCase,
    status_use_case: GetSchedulerStatusUseCase,
    reload_use_case: ReloadSchedulerUseCase
) -> APIRouter:
    """Factory function to create scheduled job router"""
    controller = ScheduledJobController(
        create_use_case=create_use_case,
        get_use_case=get_use_case,
        list_use_case=list_use_case,
        update_use_case=update_use_case,
        delete_use_case=delete_use_case,
        execute_use_case=execute_use_case,
        status_use_case=status_use_case,
        reload_use_case=reload_use_case
    )
    return controller.router
