from fastapi import FastAPI

from app.core.lifespan import lifespan
from app.domain.route import router as prediction_router

app = FastAPI(lifespan=lifespan)

app.include_router(prediction_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
