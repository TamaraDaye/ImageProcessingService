import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database.database import init_db
from .models import models


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)


@app.get("/")
async def root():
    return "Welcome"
