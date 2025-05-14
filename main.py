from fastapi import FastAPI, Depends
from .routers import user

app = FastAPI()

app.include_router(user.router)

@app.get("/")
async def root():
    return {"message": "Hello Bigger Applications!"}