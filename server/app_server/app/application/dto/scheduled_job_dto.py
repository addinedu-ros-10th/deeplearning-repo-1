"""
Scheduled Job DTOs

Data Transfer Objects for scheduled job operations.
These DTOs are used for data transfer between layers.
"""

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator


class CreateScheduledJobRequest(BaseModel):
    """Request DTO for creating a scheduled job"""
    
    name: str = Field(..., min_length=1, max_length=120, description="Job name")
    func: str = Field(..., min_length=1, max_length=200, description="Job function path")
    cron: str = Field(..., min_length=1, max_length=64, description="Cron expression")
    args: Dict[str, Any] = Field(default_factory=dict, description="Job arguments")
    kwargs: Dict[str, Any] = Field(default_factory=dict, description="Job keyword arguments")
    enabled: bool = Field(default=True, description="Whether job is enabled")
    
    @validator('name')
    def validate_name(cls, v):
        if not v or not v.strip():
            raise ValueError('Job name cannot be empty')
        return v.strip()
    
    @validator('func')
    def validate_func(cls, v):
        if not v or not v.strip():
            raise ValueError('Job function cannot be empty')
        if ':' not in v:
            raise ValueError('Job function must be in format "module:function"')
        return v.strip()
    
    @validator('cron')
    def validate_cron(cls, v):
        if not v or not v.strip():
            raise ValueError('Cron expression cannot be empty')
        return v.strip()


class UpdateScheduledJobRequest(BaseModel):
    """Request DTO for updating a scheduled job"""
    
    name: Optional[str] = Field(None, min_length=1, max_length=120, description="Job name")
    func: Optional[str] = Field(None, min_length=1, max_length=200, description="Job function path")
    cron: Optional[str] = Field(None, min_length=1, max_length=64, description="Cron expression")
    args: Optional[Dict[str, Any]] = Field(None, description="Job arguments")
    kwargs: Optional[Dict[str, Any]] = Field(None, description="Job keyword arguments")
    enabled: Optional[bool] = Field(None, description="Whether job is enabled")
    
    @validator('name')
    def validate_name(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Job name cannot be empty')
        return v.strip() if v else v
    
    @validator('func')
    def validate_func(cls, v):
        if v is not None:
            if not v or not v.strip():
                raise ValueError('Job function cannot be empty')
            if ':' not in v:
                raise ValueError('Job function must be in format "module:function"')
        return v.strip() if v else v
    
    @validator('cron')
    def validate_cron(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('Cron expression cannot be empty')
        return v.strip() if v else v


class ScheduledJobResponse(BaseModel):
    """Response DTO for scheduled job data"""
    
    id: str = Field(..., description="Job ID")
    name: str = Field(..., description="Job name")
    func: str = Field(..., description="Job function path")
    cron: str = Field(..., description="Cron expression")
    args: Dict[str, Any] = Field(..., description="Job arguments")
    kwargs: Dict[str, Any] = Field(..., description="Job keyword arguments")
    enabled: bool = Field(..., description="Whether job is enabled")
    status: str = Field(..., description="Job status")
    last_run_at: Optional[datetime] = Field(None, description="Last run time")
    next_run_at: Optional[datetime] = Field(None, description="Next run time")
    created_at: datetime = Field(..., description="Creation time")
    updated_at: datetime = Field(..., description="Last update time")
    
    class Config:
        from_attributes = True


class ScheduledJobListResponse(BaseModel):
    """Response DTO for scheduled job list"""
    
    jobs: list[ScheduledJobResponse] = Field(..., description="List of scheduled jobs")
    count: int = Field(..., description="Total count of jobs")
    timestamp: datetime = Field(..., description="Response timestamp")
    
    class Config:
        from_attributes = True


class SchedulerStatusResponse(BaseModel):
    """Response DTO for scheduler status"""
    
    scheduler_running: bool = Field(..., description="Whether scheduler is running")
    active_jobs: int = Field(..., description="Number of active jobs")
    jobs: list[Dict[str, Any]] = Field(..., description="List of active job details")
    timestamp: datetime = Field(..., description="Status timestamp")
    
    class Config:
        from_attributes = True


class JobExecutionResponse(BaseModel):
    """Response DTO for job execution"""
    
    status: str = Field(..., description="Execution status")
    message: str = Field(..., description="Execution message")
    timestamp: datetime = Field(..., description="Execution timestamp")
    
    class Config:
        from_attributes = True


class SchedulerReloadResponse(BaseModel):
    """Response DTO for scheduler reload"""
    
    status: str = Field(..., description="Reload status")
    message: str = Field(..., description="Reload message")
    jobs_reloaded: int = Field(..., description="Number of jobs reloaded")
    timestamp: datetime = Field(..., description="Reload timestamp")
    
    class Config:
        from_attributes = True


@dataclass
class JobExecutionResult:
    """Result of job execution"""
    
    success: bool
    message: str
    execution_time: float
    error: Optional[str] = None
    result: Optional[Any] = None
