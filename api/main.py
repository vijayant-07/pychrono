from fastapi import FastAPI
from api.schemas import CreateJobRequest
from fastapi.templating import Jinja2Templates
from fastapi import Request

from core.models import Job
from storage.redis_store import RedisStore
from fastapi.responses import RedirectResponse

import time
import uuid
import json

from fastapi import WebSocket

from api.websocket_manager import (
    manager
)

app = FastAPI()

store = RedisStore()

templates = Jinja2Templates(
    directory="templates"
)

@app.get("/dashboard")
async def dashboard(
    request: Request
):

    jobs = []

    for _, job_json in store.get_all_jobs().items():

        jobs.append(
            json.loads(job_json)
        )

        jobs.sort(
            key=lambda x: x["run_at"],
            reverse=True
        )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "stats": store.get_stats(),
            "jobs": jobs
        }
    )

@app.get("/")
async def root():
    return {"message": "PyChrono API"}

@app.post("/jobs")
async def create_job(req: CreateJobRequest):

    job = Job(
        id=str(uuid.uuid4()),
        task=req.task,
        payload=req.payload,
        run_at=time.time() + req.delay_seconds,

        cron=req.cron or ""
    )

    store.add_job(job)

    return {
        "job_id": job.id,
        "status": "scheduled"
    }

@app.get("/jobs")
async def get_jobs():

    jobs = []

    for _, job_json in store.get_all_jobs().items():
        jobs.append(
            json.loads(job_json)
        )

    return jobs

@app.get("/jobs/{job_id}")
async def get_job(job_id: str):
    return store.get_job(job_id)

@app.get("/jobs/status/{status}")
async def jobs_by_status(
    status: str
):

    return store.get_jobs_by_status(
        status.upper()
    )

@app.get("/stats")
async def get_stats():

    return store.get_stats()

@app.get("/jobs/{job_id}/view")
async def job_view(
    request: Request,
    job_id: str
):

    job_json = store.get_job(job_id)

    if not job_json:
        return {
            "error": "Job not found"
        }

    job = json.loads(job_json)

    return templates.TemplateResponse(
        request=request,
        name="job_details.html",
        context={
            "job": job
        }
    )

@app.post("/jobs/{job_id}/retry")
async def retry_job(job_id: str):

    success = store.requeue_job(
        job_id
    )

    if not success:
        return {
            "error": "Job not found"
        }

    return RedirectResponse(
        url="/dashboard",
        status_code=303
    )

@app.get("/dead-letter")
async def dead_letter_jobs():

    return store.get_dead_letter_jobs()

@app.get("/dashboard/dead-letter")
async def dead_letter_dashboard(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="dead_letter.html",
        context={
            "jobs": store.get_dead_letter_jobs()
        }
    )

@app.websocket("/ws")
async def websocket_endpoint(
    websocket: WebSocket
):

    await manager.connect(
        websocket
    )

    try:

        while True:
            await websocket.receive_text()

    except Exception:

        manager.disconnect(
            websocket
        )