from contextlib import asynccontextmanager

from fastapi import FastAPI

from app.core.config import get_settings
from app.core.model import get_model
from app.domain.service import Service


@asynccontextmanager
async def lifespan(app: FastAPI):
    app.title = get_settings().app_name

    # called to make sure model gets loaded into memory
    get_model()

    # called to preload snp stock predictions into cache
    await Service().predict_outperfromance_of_snp_500()

    yield
