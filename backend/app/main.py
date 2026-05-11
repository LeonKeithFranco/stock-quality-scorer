from fastapi import FastAPI

app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello, world!"}


@app.get("/health")
async def health_check():
    return {"status": "ok"}
