"""
Asynchronous database session manager using SQLAlchemy.

This module provides the session lifecycle management needed for working with a PostgreSQL database
in an asynchronous FastAPI application.
"""

import contextlib

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)

from src.conf.config import settings

class DatabaseSessionManager:
    """
    Manages asynchronous database sessions using SQLAlchemy.

    Provides an async context manager to acquire and release sessions,
    handling errors and automatic cleanup.
    """
    def __init__(self, url: str):
        """
        Initialize the database session manager with a database URL.

        Args:
            url (str): The database connection URL.
        """
        self._engine: AsyncEngine | None = create_async_engine(url)
        self._session_maker: async_sessionmaker = async_sessionmaker(
            autoflush=False, autocommit=False, bind=self._engine
        )

    @contextlib.asynccontextmanager
    async def session(self):
        """
        Provide a database session using an async context manager.

        Yields:
            AsyncSession: A SQLAlchemy asynchronous session.

        Raises:
            Exception: If the session maker is not initialized.
            SQLAlchemyError: If a database error occurs during the session.
        """
        if self._session_maker is None:
            raise Exception("Database session is not initialized")
        session = self._session_maker()
        try:
            yield session
        except SQLAlchemyError as e:
            await session.rollback()
            raise  # Re-raise the original error
        finally:
            await session.close()

sessionmanager = DatabaseSessionManager(settings.DB_URL)

async def get_db():
    """
    Dependency to inject a database session into FastAPI routes.

    Yields:
        AsyncSession: A SQLAlchemy asynchronous session for request handling.
    """
    async with sessionmanager.session() as session:
        yield session
