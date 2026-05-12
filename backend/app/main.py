from fastapi import FastAPI

from app.core.lifespan import lifespan

app = FastAPI(lifespan=lifespan)


@app.get("/health")
async def health_check():
    return {"status": "ok"}
