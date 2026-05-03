from core.models import Job
from storage.redis_store import RedisStore
import time
import uuid

store = RedisStore()

job = Job(
    id=str(uuid.uuid4()),
    task="print",
    payload={"msg": "Hello World"},
    run_at=time.time() + 5
)

store.add_job(job)

print("Job added successfully!")