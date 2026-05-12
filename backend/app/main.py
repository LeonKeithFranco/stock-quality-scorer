from fastapi import FastAPI

from app.src.core.lifespan import lifespan

app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return {"message": "Hello, world!"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
