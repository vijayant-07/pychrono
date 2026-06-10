from pydantic import BaseModel
from typing import Dict, Any
from typing import Optional

class CreateJobRequest(BaseModel):

    task: str

    payload: Dict[str, Any]

    delay_seconds: int = 0

    cron: Optional[str] = ""