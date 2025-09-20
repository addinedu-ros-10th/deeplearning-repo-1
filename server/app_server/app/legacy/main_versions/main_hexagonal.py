"""
Main Application Factory (Hexagonal Architecture)

FastAPI application factory using hexagonal architecture with DI container.
This is the new main.py that follows hexagonal architecture principles.
"""

from __future__ import annotations
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.infrastructure.settings import get_settings
from app.infrastructure.di.container import container
from app.adapters.http.scheduled_job_controller import create_scheduled_job_router


def create_app() -> FastAPI:
    """
    Create FastAPI application with hexagonal architecture.
    
    This factory function sets up the application with:
    - Dependency injection container
    - Database connections
    - HTTP routes
    - Middleware
    - Startup/shutdown events
    
    Returns:
        Configured FastAPI application
    """
    # Get settings
    settings = get_settings()
    
    # Create FastAPI app
    app = FastAPI(
        title=settings.project_name,
        version=settings.version,
        description="App Server with Hexagonal Architecture",
        debug=settings.debug
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.cors.origins,
        allow_credentials=settings.cors.allow_credentials,
        allow_methods=settings.cors.allow_methods,
        allow_headers=settings.cors.allow_headers,
    )
    
    # Setup database
    _setup_database(app, settings)
    
    # Setup dependency injection
    _setup_dependency_injection(app, settings)
    
    # Setup routes
    _setup_routes(app)
    
    # Setup startup/shutdown events
    _setup_events(app)
    
    return app


def _setup_database(app: FastAPI, settings) -> None:
    """Setup database connections"""
    
    # Create async engine for app database
    app_engine = create_async_engine(
        settings.database.app_url,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
        echo=settings.debug
    )
    
    # Create async engine for legacy database
    legacy_engine = create_async_engine(
        settings.database.legacy_url,
        pool_size=settings.database.pool_size,
        max_overflow=settings.database.max_overflow,
        echo=settings.debug
    )
    
    # Create session factories
    app_session_factory = sessionmaker(
        app_engine, class_=AsyncSession, expire_on_commit=False
    )
    legacy_session_factory = sessionmaker(
        legacy_engine, class_=AsyncSession, expire_on_commit=False
    )
    
    # Store in app state
    app.state.app_engine = app_engine
    app.state.legacy_engine = legacy_engine
    app.state.app_session_factory = app_session_factory
    app.state.legacy_session_factory = legacy_session_factory


def _setup_dependency_injection(app: FastAPI, settings) -> None:
    """Setup dependency injection container"""
    
    # Configure container
    container.config.from_dict({
        "database": {
            "app_url": settings.database.app_url,
            "legacy_url": settings.database.legacy_url,
        },
        "redis": {
            "url": settings.redis.url,
            "password": settings.redis.password,
        },
        "scheduler": {
            "timezone": settings.scheduler.timezone,
            "max_workers": settings.scheduler.max_workers,
        }
    })
    
    # Override database session provider
    container.db_session.override(
        lambda: app.state.app_session_factory()
    )
    
    # Store container in app state
    app.state.container = container


def _setup_routes(app: FastAPI) -> None:
    """Setup HTTP routes"""
    
    # Get container from app state
    container = app.state.container
    
    # Create routers
    scheduled_job_router = container.scheduled_job_router()
    
    # Include routers
    app.include_router(scheduled_job_router)
    
    # Add health check endpoint
    @app.get("/health")
    async def health_check():
        """Health check endpoint"""
        return {
            "status": "healthy",
            "service": "App Server with Hexagonal Architecture",
            "version": "1.0.0",
            "architecture": "hexagonal",
            "timestamp": "2025-09-12T12:00:00.000000"
        }
    
    # Add root endpoint
    @app.get("/")
    async def root():
        """Root endpoint"""
        return {
            "message": "App Server API with Hexagonal Architecture",
            "version": "1.0.0",
            "status": "running",
            "architecture": "hexagonal",
            "docs": "/docs",
            "admin": "/admin",
            "scheduler": "active"
        }


def _setup_events(app: FastAPI) -> None:
    """Setup startup and shutdown events"""
    
    @app.on_event("startup")
    async def startup_event():
        """Application startup event"""
        # Get container from app state
        container = app.state.container
        
        # Start scheduler
        scheduler = container.scheduler_port()
        await scheduler.start()
        
        # Store scheduler in app state
        app.state.scheduler = scheduler
        
        print("Application started with hexagonal architecture")
    
    @app.on_event("shutdown")
    async def shutdown_event():
        """Application shutdown event"""
        # Get scheduler from app state
        if hasattr(app.state, 'scheduler'):
            scheduler = app.state.scheduler
            await scheduler.stop()
        
        # Close database engines
        if hasattr(app.state, 'app_engine'):
            await app.state.app_engine.dispose()
        if hasattr(app.state, 'legacy_engine'):
            await app.state.legacy_engine.dispose()
        
        print("Application shutdown complete")


# For backward compatibility, create a function that returns the app
def get_app() -> FastAPI:
    """Get the FastAPI application instance"""
    return create_app()


# For uvicorn compatibility
app = create_app()
