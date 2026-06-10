import asyncio

from core.nats_client import NATSClient
from core.models import Job
from storage.redis_store import RedisStore

store = RedisStore()

async def process_job(job: Job):

    print(
        f"Executing job {job.id} with payload {job.payload}"
    )

    # simulate failure

    if job.payload.get("fail"):
        raise Exception("Simulated failure")


async def message_handler(msg):

    job = Job.from_json(msg.data)

    try:

        job.status = "RUNNING"
        store.update_job(job)

        await process_job(job)

        job.status = "COMPLETED"
        store.update_job(job)

        await msg.ack()

    except Exception as e:

        print("Error:", e)

        job.retries += 1

        if job.retries < job.max_retries:

            job.status = "RETRYING"

        else:

            job.status = "FAILED"

        store.update_job(job)

        await msg.ack()


async def run_worker():

    nats = NATSClient()

    await nats.connect()

    await nats.js.subscribe(
        "tasks.execute",
        durable="worker-group",
        cb=message_handler
    )

    print("Worker is listening...")

    while True:
        await asyncio.sleep(1)