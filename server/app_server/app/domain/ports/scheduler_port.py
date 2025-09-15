"""
Scheduler Port

Abstract interface for scheduler operations.
This port defines the contract for scheduler functionality.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, Callable, Any, Dict
from app.domain.entities.scheduled_job import ScheduledJob
from app.domain.value_objects.job_id import JobId


class SchedulerPort(ABC):
    """
    Abstract scheduler interface for job scheduling operations.
    
    This port defines the contract for scheduler functionality
    without depending on specific implementation details.
    """
    
    @abstractmethod
    async def start(self) -> None:
        """
        Start the scheduler
        
        Raises:
            SchedulerError: If starting fails
        """
        pass
    
    @abstractmethod
    async def stop(self) -> None:
        """
        Stop the scheduler
        
        Raises:
            SchedulerError: If stopping fails
        """
        pass
    
    @abstractmethod
    async def is_running(self) -> bool:
        """
        Check if the scheduler is running
        
        Returns:
            True if running, False otherwise
        """
        pass
    
    @abstractmethod
    async def add_job(
        self,
        job_id: JobId,
        func: Callable,
        trigger: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        **options
    ) -> None:
        """
        Add a job to the scheduler
        
        Args:
            job_id: Unique job identifier
            func: Function to execute
            trigger: Trigger expression (cron, interval, etc.)
            args: Positional arguments for the function
            kwargs: Keyword arguments for the function
            **options: Additional scheduler options
            
        Raises:
            SchedulerError: If adding job fails
        """
        pass
    
    @abstractmethod
    async def remove_job(self, job_id: JobId) -> bool:
        """
        Remove a job from the scheduler
        
        Args:
            job_id: Job identifier to remove
            
        Returns:
            True if removed successfully, False if not found
            
        Raises:
            SchedulerError: If removal fails
        """
        pass
    
    @abstractmethod
    async def get_job(self, job_id: JobId) -> Optional[Dict[str, Any]]:
        """
        Get job information
        
        Args:
            job_id: Job identifier
            
        Returns:
            Job information dictionary or None if not found
        """
        pass
    
    @abstractmethod
    async def get_jobs(self) -> List[Dict[str, Any]]:
        """
        Get all scheduled jobs
        
        Returns:
            List of job information dictionaries
        """
        pass
    
    @abstractmethod
    async def execute_job(self, job_id: JobId) -> bool:
        """
        Execute a job immediately
        
        Args:
            job_id: Job identifier to execute
            
        Returns:
            True if executed successfully, False otherwise
            
        Raises:
            SchedulerError: If execution fails
        """
        pass
    
    @abstractmethod
    async def pause_job(self, job_id: JobId) -> bool:
        """
        Pause a job
        
        Args:
            job_id: Job identifier to pause
            
        Returns:
            True if paused successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def resume_job(self, job_id: JobId) -> bool:
        """
        Resume a paused job
        
        Args:
            job_id: Job identifier to resume
            
        Returns:
            True if resumed successfully, False otherwise
        """
        pass
    
    @abstractmethod
    async def reload_jobs(self) -> int:
        """
        Reload all jobs from the repository
        
        Returns:
            Number of jobs reloaded
        """
        pass
    
    @abstractmethod
    async def get_scheduler_status(self) -> Dict[str, Any]:
        """
        Get scheduler status information
        
        Returns:
            Dictionary with scheduler status
        """
        pass
