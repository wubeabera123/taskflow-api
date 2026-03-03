from pydantic import BaseModel

class AITaskRequest(BaseModel):
    prompt: str