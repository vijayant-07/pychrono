from fastapi import FastAPI
from api.schemas import CreateJobRequest
from fastapi.templating import Jinja2Templates
from fastapi import Request

from core.models import Job
from storage.redis_store import RedisStore

import time
import uuid
import json

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
        run_at=time.time() + req.delay_seconds
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