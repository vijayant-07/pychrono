import asyncio
from core.nats_client import NATSClient
from core.models import Job

async def process_job(job: Job):
    print(f"Executing job {job.id} with payload {job.payload}")

async def message_handler(msg):
    job = Job.from_json(msg.data)

    try:
        await process_job(job)
        await msg.ack()
    except Exception as e:
        print("Error:", e)

async def run_worker():
    nats = NATSClient()
    await nats.connect()

    await nats.js.subscribe(
        "tasks.execute",
        durable="worker-group",
        cb=message_handler
    )

    print("Worker is listening...")

    # keep process alive
    while True:
        await asyncio.sleep(1)