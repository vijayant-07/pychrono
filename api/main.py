import os
import json
import time
import uuid
from datetime import datetime, timezone
import asyncio
from contextlib import asynccontextmanager

from scheduler.scheduler import run_scheduler
from worker.worker import run_worker

from fastapi import (
    FastAPI,
    Request,
    WebSocket,
    HTTPException
)

from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from starlette.middleware.sessions import SessionMiddleware
from croniter import croniter

from api.schemas import CreateJobRequest
from api.auth import oauth
from api.websocket_manager import manager

from core.models import Job
from storage.redis_store import RedisStore
from dotenv import load_dotenv

load_dotenv()

@asynccontextmanager
async def lifespan(app):

    print("Starting Scheduler...")

    asyncio.create_task(
        run_scheduler()
    )

    print("Starting Worker...")

    asyncio.create_task(
        run_worker()
    )

    yield

app = FastAPI(
    docs_url=None,
    redoc_url=None,
    lifespan=lifespan
)

store = RedisStore()

templates = Jinja2Templates(
    directory="templates"
)


SECRET_KEY = os.getenv("SECRET_KEY")

if not SECRET_KEY:
    raise ValueError(
        "SECRET_KEY not found in environment"
    )

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_KEY
)
@app.get("/")
async def login_page(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="login.html"
    )

@app.get("/login/google")
async def login_google(
    request: Request
):

    redirect_uri = (
        "https://pychrono-production.up.railway.app/auth/callback"
    )

    return await oauth.google.authorize_redirect(
        request,
        redirect_uri
    )


@app.get("/auth/callback")
async def auth_callback(
    request: Request
):

    token = await oauth.google.authorize_access_token(
        request
    )

    user = token["userinfo"]

    request.session["user"] = {

        "email": user["email"],
        "name": user["name"]

    }

    return RedirectResponse(
        "/dashboard"
    )

def get_current_user(
    request: Request
):

    user = request.session.get(
        "user"
    )

    if not user:

        return None

    return user

@app.get("/dashboard")
async def dashboard(
    request: Request
):

    user = request.session.get(
        "user"
    )

    if not user:

        return RedirectResponse("/")

    jobs = []

    for _, job_json in store.get_all_jobs().items():

        jobs.append(
            json.loads(job_json)
        )

    today = datetime.now(timezone.utc).date()

    def is_today(timestamp):

        if not timestamp:
            return False

        return datetime.fromtimestamp(
            timestamp,
            timezone.utc
        ).date() == today

    jobs_created_today = sum(
        1 for job in jobs
        if is_today(job.get("created_at"))
    )

    jobs_completed_today = sum(
        1 for job in jobs
        if is_today(job.get("completed_at"))
    )

    completed_count = sum(
        1 for job in jobs
        if job.get("status") == "COMPLETED"
    )

    failed_count = sum(
        1 for job in jobs
        if job.get("status") == "FAILED"
    )

    finished_count = completed_count + failed_count

    success_rate = round(
        (completed_count / finished_count) * 100,
        1
    ) if finished_count else 0

    jobs.sort(
        key=lambda x: x.get("run_at", 0),
        reverse=True
    )

    return templates.TemplateResponse(
        request=request,
        name="dashboard.html",
        context={
            "user": user,
            "stats": store.get_stats(),
            "jobs": jobs,
            "dashboard_metrics": {
                "success_rate": success_rate,
                "failed_jobs": failed_count,
                "jobs_created_today": jobs_created_today,
                "jobs_completed_today": jobs_completed_today
            },
            "chart_data": {
                "success": completed_count,
                "failed": failed_count
            }
        }
    )

@app.get("/logout")
async def logout(
    request: Request
):

    request.session.clear()

    return RedirectResponse("/")

@app.post("/jobs")
async def create_job(req: CreateJobRequest):

    created_at = time.time()
    cron = req.cron or ""

    try:
        run_at = (
            croniter(
                cron,
                datetime.now()
            ).get_next()
            if cron
            else created_at + req.delay_seconds
        )
    except Exception:
        raise HTTPException(
            status_code=400,
            detail="Invalid cron expression"
        )

    job = Job(
        id=str(uuid.uuid4()),
        task=req.task,
        payload=req.payload,
        run_at=run_at,

        cron=cron,
        created_at=created_at
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

    user = get_current_user(
        request
    )

    if not user:

        return RedirectResponse("/")

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
            "job": job,
            "user": user
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

@app.get("/dashboard/dead-letter")
async def dead_letter_dashboard(
    request: Request
):

    user = get_current_user(
        request
    )

    if not user:

        return RedirectResponse("/")

    return templates.TemplateResponse(
        request=request,
        name="dead_letter.html",
        context={
            "jobs": store.get_dead_letter_jobs(),
            "user": user
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
