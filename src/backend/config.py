"""
Configuration module for database initialization strategies and dependency injection.

This module provides:
- Factory pattern for creating FastAPI applications with different initialization strategies
- Dependency injection functions for FastAPI routes to access database resources
"""

from abc import ABC, abstractmethod
from typing import Callable
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
from pathlib import Path
import os
from pymongo.collection import Collection


# ============================================================================
# Database Initialization Strategies (Factory Pattern)
# ============================================================================

class DatabaseInitStrategy(ABC):
    """Abstract base class for database initialization strategies."""

    @abstractmethod
    def initialize(self) -> None:
        """Initialize the database according to the strategy."""
        pass


class ProductionDatabaseInit(DatabaseInitStrategy):
    """Production strategy: Initialize database with sample data."""

    def __init__(self, database_module):
        self.database = database_module

    def initialize(self) -> None:
        """Initialize database with sample data in production."""
        self.database.init_database()


class TestingDatabaseInit(DatabaseInitStrategy):
    """Testing strategy: Skip initialization (handled by test fixtures)."""

    def initialize(self) -> None:
        """No-op initialization for testing."""
        pass


# ============================================================================
# Dependency Injection Functions
# ============================================================================

def get_activities_collection() -> Collection:
    """
    FastAPI dependency: Provides activities collection.

    **Lifecycle and Resolution:**
    - Resolved once per request (FastAPI default)
    - Imported on first call, subsequent calls use cached module reference
    - All requests within the same process share the same underlying MongoDB connection

    **Side Effects:**
    - First call triggers module import (one-time)
    - No side effects on subsequent calls
    - Accesses global database connection created at module load time

    **Caching Behavior:**
    - Returns the same Collection instance for all requests in the same process
    - MongoDB connection pooling handles concurrent request safety
    - Thread-safe: PyMongo client manages connection pool internally

    **Usage in Routes:**
    - Use with FastAPI Depends(): `Depends(get_activities_collection)`
    - Enables inversion of control and simplifies testing via mocking

    Returns:
        MongoDB Collection object for activities data (singleton per process)
    """
    from backend import database
    return database.activities_collection


def get_teachers_collection() -> Collection:
    """
    FastAPI dependency: Provides teachers collection.

    **Lifecycle and Resolution:**
    - Resolved once per request (FastAPI default)
    - Imported on first call, subsequent calls use cached module reference
    - All requests within the same process share the same underlying MongoDB connection

    **Side Effects:**
    - First call triggers module import (one-time)
    - No side effects on subsequent calls
    - Accesses global database connection created at module load time

    **Caching Behavior:**
    - Returns the same Collection instance for all requests in the same process
    - MongoDB connection pooling handles concurrent request safety
    - Thread-safe: PyMongo client manages connection pool internally

    **Usage in Routes:**
    - Use with FastAPI Depends(): `Depends(get_teachers_collection)`
    - Enables inversion of control and simplifies testing via mocking

    Returns:
        MongoDB Collection object for teachers data (singleton per process)
    """
    from backend import database
    return database.teachers_collection


def get_announcements_collection() -> Collection:
    """
    FastAPI dependency: Provides announcements collection.

    **Lifecycle and Resolution:**
    - Resolved once per request (FastAPI default)
    - Imported on first call, subsequent calls use cached module reference
    - All requests within the same process share the same underlying MongoDB connection

    **Side Effects:**
    - First call triggers module import (one-time)
    - No side effects on subsequent calls
    - Accesses global database connection created at module load time

    **Caching Behavior:**
    - Returns the same Collection instance for all requests in the same process
    - MongoDB connection pooling handles concurrent request safety
    - Thread-safe: PyMongo client manages connection pool internally

    **Usage in Routes:**
    - Use with FastAPI Depends(): `Depends(get_announcements_collection)`
    - Enables inversion of control and simplifies testing via mocking

    Returns:
        MongoDB Collection object for announcements data (singleton per process)
    """
    from backend import database
    return database.announcements_collection


def get_verify_password() -> Callable[[str, str], bool]:
    """
    FastAPI dependency: Provides password verification function.

    **Lifecycle and Resolution:**
    - Resolved once per request (FastAPI default)
    - Imported on first call, subsequent calls return cached function reference
    - Callable is stateless and reusable across requests

    **Side Effects:**
    - First call triggers module import (one-time)
    - No side effects on invocation (pure function)
    - Password verification is CPU-intensive (Argon2) but deterministic

    **Caching Behavior:**
    - Returns the same function reference for all requests in the same process
    - Function reference caching reduces import overhead
    - Each call to the returned function is independent (no shared state)

    **Security Considerations:**
    - Uses constant-time comparison (Argon2 library)
    - Does not cache verification results (prevents timing attacks)
    - Each verification performs full Argon2 computation

    **Performance Notes:**
    - Argon2 intentionally slow (0.1-1s per verification)
    - Not suitable for high-frequency verification (e.g., rate limiting)
    - Acceptable for login endpoint (typically < 10 req/sec per user)

    **Usage in Routes:**
    - Use with FastAPI Depends(): `verify_password = Depends(get_verify_password)`
    - Inject into endpoints that require password authentication

    Returns:
        Callable password verification function with signature:
        verify_password(hashed_password: str, plain_password: str) -> bool

        Parameters of returned function:
            hashed_password (str): The Argon2 hashed password (from database)
            plain_password (str): The plain text password to verify (from user input)

        Returns from callable:
            bool: True if plain_password matches hashed_password, False otherwise

        Example usage:
            verify_pwd = Depends(get_verify_password)
            is_valid = verify_pwd(stored_hash, user_input)
    """
    from backend import database
    return database.verify_password


# ============================================================================
# Application Factory
# ============================================================================

def create_app(db_init_strategy: DatabaseInitStrategy) -> FastAPI:
    """
    Create and configure the FastAPI application.

    Args:
        db_init_strategy: Strategy for initializing the database

    Returns:
        Configured FastAPI application instance
    """
    from backend import routers

    # Initialize web host
    app = FastAPI(
        title="Mergington High School API",
        description="API for viewing and signing up for extracurricular activities"
    )

    # Initialize database using the provided strategy
    db_init_strategy.initialize()

    # Mount the static files directory for serving the frontend
    current_dir = Path(__file__).parent.parent
    app.mount("/static", StaticFiles(directory=os.path.join(current_dir, "static")), name="static")

    # Root endpoint to redirect to static index.html
    @app.get("/")
    def root():
        return RedirectResponse(url="/static/index.html")

    # Include routers
    app.include_router(routers.activities.router)
    app.include_router(routers.auth.router)
    app.include_router(routers.announcements.router)

    return app
