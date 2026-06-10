from dataclasses import dataclass
import json

@dataclass
class Job:
    id: str
    task: str
    payload: dict
    run_at: float

    status: str = "PENDING"

    retries: int = 0
    max_retries: int = 3

    last_error: str = ""

    cron: str = ""

    created_at: float = 0.0
    completed_at: float = 0.0
    failed_at: float = 0.0

    def to_json(self):
        return json.dumps(self.__dict__).encode()

    @staticmethod
    def from_json(data):

        if isinstance(data, bytes):
            data = data.decode()

        return Job(**json.loads(data))
