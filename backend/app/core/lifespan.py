from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.model import get_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application start up and shutdown lifecycle.

    Sets the application title from settings and preloads the ML model into memory so the
    first prediction request is not delayed.

    Args:
        app: The FastAPI application instance.
    """
    app.title = get_settings().app_name

    # called to make sure model gets loaded into memory
    get_model()

    yield
