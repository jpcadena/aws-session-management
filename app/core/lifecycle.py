"""
A module for lifecycle in the app-core package.
"""

import logging
from contextlib import asynccontextmanager
from typing import Any, AsyncGenerator

from fastapi import FastAPI

from app.config.config import get_init_settings, get_settings

logger: logging.Logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(application: FastAPI) -> AsyncGenerator[Any, None]:
    """
    The lifespan of the application

    :param application: The FastAPI application
    :type application: FastAPI
    :return: An synchronous generator for the application
    :rtype: Generator[Any, None]
    """
    logger.info("Starting API...")
    try:
        application.state.init_settings = get_init_settings()
        application.state.settings = get_settings()
        logger.info("Configuration settings loaded.")
        yield
    except Exception as exc:
        logger.error(f"Error during application startup: {exc}")
        raise
    finally:
        logger.info("Application shutdown completed.")
