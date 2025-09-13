"""
Scheduler Domain Service

Contains business logic that doesn't naturally fit into entities.
This service operates on domain objects and enforces business rules.
"""

from __future__ import annotations
from typing import List, Optional
from datetime import datetime, timedelta
from app.domain.entities.scheduled_job import ScheduledJob, JobStatus
from app.domain.value_objects.job_id import CronExpression, JobName


class SchedulerDomainService:
    """
    Scheduler Domain Service
    
    Contains business logic for scheduling operations that don't belong
    to individual entities but are part of the domain.
    """
    
    def __init__(self):
        pass
    
    def validate_job_schedule(self, job: ScheduledJob) -> bool:
        """
        Validate if a job can be scheduled based on business rules
        
        Args:
            job: The scheduled job to validate
            
        Returns:
            True if the job can be scheduled, False otherwise
        """
        # Check if job is enabled
        if not job.enabled:
            return False
        
        # Check if job is in a runnable state
        if not job.is_runnable():
            return False
        
        # Check if cron expression is valid
        try:
            CronExpression(job.cron)
        except ValueError:
            return False
        
        # Check if function name is valid
        try:
            JobName(job.name)
        except ValueError:
            return False
        
        return True
    
    def calculate_next_run_time(self, cron_expr: str, last_run: Optional[datetime] = None) -> Optional[datetime]:
        """
        Calculate the next run time for a job based on cron expression
        
        Args:
            cron_expr: Cron expression string
            last_run: Last run time (optional)
            
        Returns:
            Next run time or None if calculation fails
        """
        try:
            # This is a simplified implementation
            # In a real implementation, you would use a proper cron parser
            # like croniter or apscheduler's CronTrigger
            
            # For now, return a placeholder
            base_time = last_run or datetime.utcnow()
            return base_time + timedelta(minutes=5)  # Placeholder: run every 5 minutes
            
        except Exception:
            return None
    
    def can_job_run_now(self, job: ScheduledJob) -> bool:
        """
        Check if a job can run at the current time
        
        Args:
            job: The scheduled job to check
            
        Returns:
            True if the job can run now, False otherwise
        """
        if not self.validate_job_schedule(job):
            return False
        
        # Check if job is not currently running
        if job.status == JobStatus.RUNNING:
            return False
        
        # Check if enough time has passed since last run
        if job.last_run_at:
            time_since_last_run = datetime.utcnow() - job.last_run_at
            if time_since_last_run < timedelta(seconds=30):  # Minimum 30 seconds between runs
                return False
        
        return True
    
    def get_jobs_ready_to_run(self, jobs: List[ScheduledJob]) -> List[ScheduledJob]:
        """
        Get all jobs that are ready to run
        
        Args:
            jobs: List of all scheduled jobs
            
        Returns:
            List of jobs that are ready to run
        """
        ready_jobs = []
        
        for job in jobs:
            if self.can_job_run_now(job):
                ready_jobs.append(job)
        
        return ready_jobs
    
    def validate_job_function(self, func_name: str) -> bool:
        """
        Validate if a job function name is properly formatted
        
        Args:
            func_name: Function name in format 'module:function'
            
        Returns:
            True if valid, False otherwise
        """
        if not func_name or ':' not in func_name:
            return False
        
        parts = func_name.split(':')
        if len(parts) != 2:
            return False
        
        module_name, function_name = parts
        
        # Basic validation
        if not module_name or not function_name:
            return False
        
        # Check if module and function names are valid Python identifiers
        import re
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_.]*$', module_name):
            return False
        
        if not re.match(r'^[a-zA-Z_][a-zA-Z0-9_]*$', function_name):
            return False
        
        return True
    
    def get_job_execution_summary(self, jobs: List[ScheduledJob]) -> dict:
        """
        Get a summary of job execution statistics
        
        Args:
            jobs: List of all scheduled jobs
            
        Returns:
            Dictionary with execution statistics
        """
        total_jobs = len(jobs)
        enabled_jobs = len([j for j in jobs if j.enabled])
        disabled_jobs = total_jobs - enabled_jobs
        
        status_counts = {}
        for status in JobStatus:
            status_counts[status.value] = len([j for j in jobs if j.status == status])
        
        return {
            'total_jobs': total_jobs,
            'enabled_jobs': enabled_jobs,
            'disabled_jobs': disabled_jobs,
            'status_breakdown': status_counts,
            'last_updated': datetime.utcnow().isoformat()
        }
