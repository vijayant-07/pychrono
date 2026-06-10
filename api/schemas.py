from pydantic import BaseModel
from typing import Dict, Any

class CreateJobRequest(BaseModel):
    task: str
    payload: Dict[str, Any]
    delay_seconds: int