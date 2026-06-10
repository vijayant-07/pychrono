import asyncio
import time

from core.nats_client import NATSClient
from core.models import Job
from storage.redis_store import RedisStore
from core.events import (
    publish_job_event
)
from croniter import croniter
from datetime import datetime

store = RedisStore()


async def process_job(job: Job):

    if job.payload.get("fail"):
        raise Exception(
            "Simulated failure"
        )

    print(
        f"Executing job {job.id}"
    )


async def message_handler(msg):

    job = Job.from_json(msg.data)

    try:

        job.status = "RUNNING"
        store.update_job(job)

        await process_job(job)

        if job.cron:

            next_run = croniter(
                job.cron,
                datetime.now()
            ).get_next()

            job.run_at = next_run

            job.status = "PENDING"

            store.add_job(job)

            store.update_job(job)

            print(
                f"Cron job rescheduled: "
                f"{job.id}"
            )

        else:

            job.status = "COMPLETED"
            job.completed_at = time.time()

            store.update_job(job)

        print(
            f"Job completed: {job.id}"
        )

        await msg.ack()

    except Exception as e:

        print(
            f"Job failed: {job.id}"
        )

        print(
            f"Error: {e}"
        )

        job.retries += 1

        if job.retries < job.max_retries:

            print(
                f"Retrying job {job.id} "
                f"({job.retries}/{job.max_retries})"
            )

            job.status = "PENDING"

            # retry after 10 seconds
            job.run_at = time.time() + 10

            # add back to scheduler queue
            store.add_job(job)

            # update metadata
            store.update_job(job)

        else:

            print(
                f"Job permanently failed: {job.id}"
            )

            job.status = "FAILED"

            job.last_error = str(e)
            job.failed_at = time.time()

            store.update_job(job)

            store.move_to_dlq(job)

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
