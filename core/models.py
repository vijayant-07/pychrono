from dataclasses import dataclass
import time
import json

@dataclass
class Job:
    id: str
    task: str
    payload: dict
    run_at: float

    def to_json(self):
        return json.dumps(self.__dict__).encode()

    @staticmethod
    def from_json(data):
        return Job(**json.loads(data))