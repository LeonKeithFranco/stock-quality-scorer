from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.model import get_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.title = get_settings().app_name

    # called to make sure model gets loaded into memory
    get_model()

    yield
