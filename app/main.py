from fastapi import FastAPI
from app.routers import tasks
from app.routers import auth
from app.services.prisma import db
from dotenv import load_dotenv
load_dotenv()  # Load environment variables from .env file

app = FastAPI()

app.include_router(tasks.router)

app.include_router(auth.router)

@app.on_event("startup")
async def startup():
    await db.connect()


@app.on_event("shutdown")
async def shutdown():
    await db.disconnect()
