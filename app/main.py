from fastapi import FastAPI
from dotenv import load_dotenv
from app.routers import tasks, auth, ai
from app.core.database import engine, Base

load_dotenv()

app = FastAPI()

app.include_router(tasks.router)
app.include_router(auth.router)
app.include_router(ai.router)



# @app.on_event("startup")
# async def on_startup():
#     async with engine.begin() as conn:
#         await conn.run_sync(Base.metadata.create_all)


@app.on_event("shutdown")
async def on_shutdown():
    await engine.dispose()