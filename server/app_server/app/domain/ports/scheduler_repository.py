"""
Scheduler Repository Port

Abstract interface for scheduled job repository operations.
This port defines the contract that adapters must implement.
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional
from app.domain.entities.scheduled_job import ScheduledJob
from app.domain.value_objects.job_id import JobId


class SchedulerRepository(ABC):
    """
    Abstract repository interface for scheduled job operations.
    
    This port defines the contract for data access operations
    without depending on specific implementation details.
    """
    
    @abstractmethod
    async def create(self, job: ScheduledJob) -> ScheduledJob:
        """
        Create a new scheduled job
        
        Args:
            job: The scheduled job to create
            
        Returns:
            The created scheduled job
            
        Raises:
            RepositoryError: If creation fails
        """
        pass
    
    @abstractmethod
    async def get_by_id(self, job_id: JobId) -> Optional[ScheduledJob]:
        """
        Get a scheduled job by ID
        
        Args:
            job_id: The job ID
            
        Returns:
            The scheduled job if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_by_name(self, name: str) -> Optional[ScheduledJob]:
        """
        Get a scheduled job by name
        
        Args:
            name: The job name
            
        Returns:
            The scheduled job if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def get_all(self) -> List[ScheduledJob]:
        """
        Get all scheduled jobs
        
        Returns:
            List of all scheduled jobs
        """
        pass
    
    @abstractmethod
    async def get_enabled(self) -> List[ScheduledJob]:
        """
        Get all enabled scheduled jobs
        
        Returns:
            List of enabled scheduled jobs
        """
        pass
    
    @abstractmethod
    async def update(self, job: ScheduledJob) -> ScheduledJob:
        """
        Update an existing scheduled job
        
        Args:
            job: The scheduled job to update
            
        Returns:
            The updated scheduled job
            
        Raises:
            RepositoryError: If update fails
        """
        pass
    
    @abstractmethod
    async def delete(self, job_id: JobId) -> bool:
        """
        Delete a scheduled job
        
        Args:
            job_id: The job ID to delete
            
        Returns:
            True if deleted successfully, False otherwise
            
        Raises:
            RepositoryError: If deletion fails
        """
        pass
    
    @abstractmethod
    async def exists(self, job_id: JobId) -> bool:
        """
        Check if a scheduled job exists
        
        Args:
            job_id: The job ID to check
            
        Returns:
            True if exists, False otherwise
        """
        pass
    
    @abstractmethod
    async def count(self) -> int:
        """
        Get the total count of scheduled jobs
        
        Returns:
            Total count of scheduled jobs
        """
        pass
