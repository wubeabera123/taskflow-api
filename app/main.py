from fastapi import FastAPI
from app.routers import tasks
from app.services.prisma import db

app = FastAPI()

app.include_router(tasks.router)


@app.on_event("startup")
async def startup():
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()
