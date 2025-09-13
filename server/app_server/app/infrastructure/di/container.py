"""
Dependency Injection Container

DI container configuration using dependency-injector.
This container manages all dependencies and their lifecycle.
"""

from __future__ import annotations
from dependency_injector import containers, providers
from sqlalchemy.ext.asyncio import AsyncSession
from app.domain.services.scheduler_domain_service import SchedulerDomainService
from app.domain.ports.scheduler_repository import SchedulerRepository
from app.domain.ports.scheduler_port import SchedulerPort
from app.adapters.repositories.scheduled_job_repository_impl import ScheduledJobRepositoryImpl
from app.adapters.scheduler.apscheduler_adapter import APSchedulerAdapter
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
from app.adapters.http.scheduled_job_controller import create_scheduled_job_router


class Container(containers.DeclarativeContainer):
    """
    Dependency injection container.
    
    This container manages all dependencies and their lifecycle.
    """
    
    # Configuration
    config = providers.Configuration()
    
    # Database session
    db_session = providers.Dependency(instance_of=AsyncSession)
    
    # Domain services
    scheduler_domain_service = providers.Factory(
        SchedulerDomainService
    )
    
    # Ports (interfaces)
    scheduler_repository = providers.Factory(
        ScheduledJobRepositoryImpl,
        session=db_session
    )
    
    scheduler_port = providers.Factory(
        APSchedulerAdapter
    )
    
    # Use cases
    create_scheduled_job_use_case = providers.Factory(
        CreateScheduledJobUseCase,
        repository=scheduler_repository,
        scheduler=scheduler_port,
        domain_service=scheduler_domain_service
    )
    
    get_scheduled_job_use_case = providers.Factory(
        GetScheduledJobUseCase,
        repository=scheduler_repository
    )
    
    list_scheduled_jobs_use_case = providers.Factory(
        ListScheduledJobsUseCase,
        repository=scheduler_repository
    )
    
    update_scheduled_job_use_case = providers.Factory(
        UpdateScheduledJobUseCase,
        repository=scheduler_repository,
        scheduler=scheduler_port,
        domain_service=scheduler_domain_service
    )
    
    delete_scheduled_job_use_case = providers.Factory(
        DeleteScheduledJobUseCase,
        repository=scheduler_repository,
        scheduler=scheduler_port
    )
    
    execute_scheduled_job_use_case = providers.Factory(
        ExecuteScheduledJobUseCase,
        scheduler=scheduler_port
    )
    
    get_scheduler_status_use_case = providers.Factory(
        GetSchedulerStatusUseCase,
        scheduler=scheduler_port
    )
    
    reload_scheduler_use_case = providers.Factory(
        ReloadSchedulerUseCase,
        repository=scheduler_repository,
        scheduler=scheduler_port,
        domain_service=scheduler_domain_service
    )
    
    # HTTP controllers
    scheduled_job_router = providers.Factory(
        create_scheduled_job_router,
        create_use_case=create_scheduled_job_use_case,
        get_use_case=get_scheduled_job_use_case,
        list_use_case=list_scheduled_jobs_use_case,
        update_use_case=update_scheduled_job_use_case,
        delete_use_case=delete_scheduled_job_use_case,
        execute_use_case=execute_scheduled_job_use_case,
        status_use_case=get_scheduler_status_use_case,
        reload_use_case=reload_scheduler_use_case
    )


# Global container instance
container = Container()
