"""
Scheduled Job Domain Entity

This entity represents a scheduled job in the domain layer.
It contains business logic and validation rules.
"""

from __future__ import annotations
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass
from enum import Enum


class JobStatus(Enum):
    """Job execution status"""
    IDLE = "idle"
    RUNNING = "running"
    SUCCESS = "success"
    FAILED = "failed"
    DISABLED = "disabled"


@dataclass
class ScheduledJob:
    """
    Scheduled Job Domain Entity
    
    Represents a scheduled job with business rules and validation.
    This is the core domain entity that encapsulates business logic.
    """
    
    id: str
    name: str
    func: str
    cron: str
    args: Dict[str, Any]
    kwargs: Dict[str, Any]
    enabled: bool
    status: JobStatus
    last_run_at: Optional[datetime]
    next_run_at: Optional[datetime]
    created_at: datetime
    updated_at: datetime
    
    def __post_init__(self):
        """Validate entity after initialization"""
        self._validate()
    
    def _validate(self) -> None:
        """Validate business rules"""
        if not self.name or len(self.name.strip()) == 0:
            raise ValueError("Job name cannot be empty")
        
        if not self.func or len(self.func.strip()) == 0:
            raise ValueError("Job function cannot be empty")
        
        if not self.cron or len(self.cron.strip()) == 0:
            raise ValueError("Job cron expression cannot be empty")
        
        if self.args is None:
            self.args = {}
        
        if self.kwargs is None:
            self.kwargs = {}
    
    def enable(self) -> None:
        """Enable the job"""
        self.enabled = True
        self.status = JobStatus.IDLE
        self.updated_at = datetime.utcnow()
    
    def disable(self) -> None:
        """Disable the job"""
        self.enabled = False
        self.status = JobStatus.DISABLED
        self.updated_at = datetime.utcnow()
    
    def mark_as_running(self) -> None:
        """Mark job as running"""
        if not self.enabled:
            raise ValueError("Cannot run disabled job")
        self.status = JobStatus.RUNNING
        self.updated_at = datetime.utcnow()
    
    def mark_as_success(self) -> None:
        """Mark job as successfully completed"""
        self.status = JobStatus.SUCCESS
        self.last_run_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def mark_as_failed(self) -> None:
        """Mark job as failed"""
        self.status = JobStatus.FAILED
        self.last_run_at = datetime.utcnow()
        self.updated_at = datetime.utcnow()
    
    def update_schedule(self, cron: str) -> None:
        """Update job schedule"""
        if not cron or len(cron.strip()) == 0:
            raise ValueError("Cron expression cannot be empty")
        
        self.cron = cron
        self.updated_at = datetime.utcnow()
    
    def update_function(self, func: str) -> None:
        """Update job function"""
        if not func or len(func.strip()) == 0:
            raise ValueError("Job function cannot be empty")
        
        self.func = func
        self.updated_at = datetime.utcnow()
    
    def is_runnable(self) -> bool:
        """Check if job can be run"""
        return self.enabled and self.status in [JobStatus.IDLE, JobStatus.SUCCESS, JobStatus.FAILED]
    
    def __str__(self) -> str:
        return f"ScheduledJob(id={self.id}, name={self.name}, status={self.status.value})"
    
    def __repr__(self) -> str:
        return self.__str__()
