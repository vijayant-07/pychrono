import asyncio

from api.websocket_manager import (
    manager
)

async def publish_job_event(
    job
):

    await manager.broadcast(
        {
            "job_id": job.id,
            "status": job.status,
            "retries": job.retries
        }
    )