from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.model import get_model


@asynccontextmanager
async def lifespan(app: FastAPI):
    # called to make sure model gets loaded into memory
    get_model()

    yield
