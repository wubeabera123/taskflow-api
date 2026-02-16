from fastapi import FastAPI
from app.routers import tasks


app = FastAPI()
app = FastAPI(title="TaskFlow API")

app.include_router(tasks.router)

@app.get("/")
def home():
    return {"message": "TaskFlow API is running"}
