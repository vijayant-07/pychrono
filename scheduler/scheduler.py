import asyncio

from core.nats_client import NATSClient
from core.models import Job
from storage.redis_store import RedisStore

store = RedisStore()

async def run_scheduler():

    nats = NATSClient()

    await nats.connect()
    try:
        await nats.setup_stream()
    except Exception:
        pass

    while True:

        jobs = store.get_due_jobs()

        for job_str in jobs:

            job = Job.from_json(job_str)

            job.status = "DISPATCHED"

            store.update_job(job)

            print(f"Dispatching job: {job.id}")

            await nats.publish(
                "tasks.execute",
                job.to_json()
            )

        await asyncio.sleep(1)