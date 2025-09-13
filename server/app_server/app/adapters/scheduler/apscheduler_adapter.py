"""
APScheduler Adapter

APScheduler implementation of the scheduler port.
This adapter implements the scheduler interface using APScheduler.
"""

from __future__ import annotations
from typing import List, Optional, Callable, Any, Dict
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from apscheduler.triggers.interval import IntervalTrigger
from apscheduler.triggers.date import DateTrigger
from apscheduler.job import Job
from app.domain.value_objects.job_id import JobId
from app.domain.ports.scheduler_port import SchedulerPort


class APSchedulerAdapter(SchedulerPort):
    """
    APScheduler implementation of the scheduler port.
    
    This adapter implements the scheduler interface using APScheduler.
    """
    
    def __init__(self):
        self.scheduler = AsyncIOScheduler()
        self._is_running = False
    
    async def start(self) -> None:
        """Start the scheduler"""
        try:
            if not self._is_running:
                self.scheduler.start()
                self._is_running = True
        except Exception as e:
            raise SchedulerError(f"Failed to start scheduler: {str(e)}")
    
    async def stop(self) -> None:
        """Stop the scheduler"""
        try:
            if self._is_running:
                self.scheduler.shutdown()
                self._is_running = False
        except Exception as e:
            raise SchedulerError(f"Failed to stop scheduler: {str(e)}")
    
    async def is_running(self) -> bool:
        """Check if the scheduler is running"""
        return self._is_running and self.scheduler.running
    
    async def add_job(
        self,
        job_id: JobId,
        func: Callable,
        trigger: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None,
        **options
    ) -> None:
        """Add a job to the scheduler"""
        try:
            # Parse trigger
            trigger_obj = self._parse_trigger(trigger)
            
            # Add job to scheduler
            self.scheduler.add_job(
                func=func,
                trigger=trigger_obj,
                id=job_id.value,
                args=args or [],
                kwargs=kwargs or {},
                **options
            )
        except Exception as e:
            raise SchedulerError(f"Failed to add job: {str(e)}")
    
    async def remove_job(self, job_id: JobId) -> bool:
        """Remove a job from the scheduler"""
        try:
            self.scheduler.remove_job(job_id.value)
            return True
        except Exception as e:
            # Job might not exist
            return False
    
    async def get_job(self, job_id: JobId) -> Optional[Dict[str, Any]]:
        """Get job information"""
        try:
            job = self.scheduler.get_job(job_id.value)
            if job is None:
                return None
            
            return self._job_to_dict(job)
        except Exception as e:
            raise SchedulerError(f"Failed to get job: {str(e)}")
    
    async def get_jobs(self) -> List[Dict[str, Any]]:
        """Get all scheduled jobs"""
        try:
            jobs = self.scheduler.get_jobs()
            return [self._job_to_dict(job) for job in jobs]
        except Exception as e:
            raise SchedulerError(f"Failed to get jobs: {str(e)}")
    
    async def execute_job(self, job_id: JobId) -> bool:
        """Execute a job immediately"""
        try:
            job = self.scheduler.get_job(job_id.value)
            if job is None:
                return False
            
            # Execute job immediately
            job.modify(next_run_time=None)
            return True
        except Exception as e:
            raise SchedulerError(f"Failed to execute job: {str(e)}")
    
    async def pause_job(self, job_id: JobId) -> bool:
        """Pause a job"""
        try:
            job = self.scheduler.get_job(job_id.value)
            if job is None:
                return False
            
            job.pause()
            return True
        except Exception as e:
            raise SchedulerError(f"Failed to pause job: {str(e)}")
    
    async def resume_job(self, job_id: JobId) -> bool:
        """Resume a paused job"""
        try:
            job = self.scheduler.get_job(job_id.value)
            if job is None:
                return False
            
            job.resume()
            return True
        except Exception as e:
            raise SchedulerError(f"Failed to resume job: {str(e)}")
    
    async def reload_jobs(self) -> int:
        """Reload all jobs from the repository"""
        try:
            # This is a placeholder implementation
            # In a real implementation, you would reload jobs from the repository
            # For now, return the current job count
            return len(self.scheduler.get_jobs())
        except Exception as e:
            raise SchedulerError(f"Failed to reload jobs: {str(e)}")
    
    async def get_scheduler_status(self) -> Dict[str, Any]:
        """Get scheduler status information"""
        try:
            return {
                'running': self.scheduler.running,
                'job_count': len(self.scheduler.get_jobs()),
                'next_run_time': self.scheduler.next_run_time,
                'state': self.scheduler.state
            }
        except Exception as e:
            raise SchedulerError(f"Failed to get scheduler status: {str(e)}")
    
    def _parse_trigger(self, trigger: str):
        """Parse trigger string into APScheduler trigger object"""
        if trigger.startswith('cron:'):
            # Cron trigger: "cron:*/5 * * * *"
            cron_expr = trigger[5:]  # Remove "cron:" prefix
            return CronTrigger.from_crontab(cron_expr)
        elif trigger.startswith('interval:'):
            # Interval trigger: "interval:300" (seconds)
            seconds = int(trigger[9:])  # Remove "interval:" prefix
            return IntervalTrigger(seconds=seconds)
        elif trigger.startswith('date:'):
            # Date trigger: "date:2023-12-31 23:59:59"
            date_str = trigger[5:]  # Remove "date:" prefix
            from datetime import datetime
            run_date = datetime.fromisoformat(date_str)
            return DateTrigger(run_date=run_date)
        else:
            # Assume it's a cron expression
            return CronTrigger.from_crontab(trigger)
    
    def _job_to_dict(self, job: Job) -> Dict[str, Any]:
        """Convert APScheduler job to dictionary"""
        return {
            'id': job.id,
            'name': job.name,
            'func': str(job.func),
            'trigger': str(job.trigger),
            'next_run_time': job.next_run_time.isoformat() if job.next_run_time else None,
            'args': job.args,
            'kwargs': job.kwargs
        }


class SchedulerError(Exception):
    """Scheduler operation error"""
    pass
