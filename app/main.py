from contextlib import asynccontextmanager
from fastapi import FastAPI
from .database.database import init_db
from .models import models
from .routers import users, authentication, images


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(lifespan=lifespan)

app.include_router(users.router)
app.include_router(authentication.router)
app.include_router(images.router)


@app.get("/")
async def root():
    return "Welcome"
