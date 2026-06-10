import json
import time
import os
import redis


REDIS_URL = os.getenv("REDIS_URL")

if REDIS_URL:

    print("Using Railway Redis")

    r = redis.from_url(
        REDIS_URL,
        decode_responses=True
    )

else:

    REDIS_HOST = os.getenv(
        "REDIS_HOST",
        "localhost"
    )

    print(
        f"Using Local Redis: {REDIS_HOST}"
    )

    r = redis.Redis(
        host=REDIS_HOST,
        port=6379,
        decode_responses=True
    )
print("Redis client initialized")

class RedisStore:

    def add_job(self, job):

        r.zadd(
            "jobs",
            {json.dumps(job.__dict__): job.run_at}
        )

        r.hset(
            "job_details",
            job.id,
            json.dumps(job.__dict__)
        )

    def get_due_jobs(self):

        now = time.time()

        jobs = r.zrangebyscore(
            "jobs",
            0,
            now
        )

        if jobs:
            r.zremrangebyscore(
                "jobs",
                0,
                now
            )

        return jobs

    def get_all_jobs(self):
        return r.hgetall("job_details")

    def get_job(self, job_id):
        return r.hget("job_details", job_id)

    def update_job(self, job):

        r.hset(
            "job_details",
            job.id,
            json.dumps(job.__dict__)
        )

    def update_status(self, job_id, status):

        job_json = r.hget(
            "job_details",
            job_id
        )

        if not job_json:
            return

        job = json.loads(job_json)

        job["status"] = status

        r.hset(
            "job_details",
            job_id,
            json.dumps(job)
        )

    def get_jobs_by_status(self, status):

        jobs = []

        for _, job_json in self.get_all_jobs().items():

            job = json.loads(job_json)

            if job["status"] == status:
                jobs.append(job)

        return jobs
    
    def get_stats(self):

        stats = {
            "PENDING": 0,
            "DISPATCHED": 0,
            "RUNNING": 0,
            "RETRYING": 0,
            "COMPLETED": 0,
            "FAILED": 0,
            "CRON": 0
        }

        jobs = self.get_all_jobs()

        for _, job_json in jobs.items():

            job = json.loads(job_json)

            status = job.get(
                "status",
                "PENDING"
            )

            if status not in stats:
                stats[status] = 0

            stats[status] += 1

            if job.get("cron"):
                stats["CRON"] += 1

        return stats
    
    def requeue_job(self, job_id):

        job_json = self.get_job(job_id)

        if not job_json:
            return False

        job = json.loads(job_json)

        job["status"] = "PENDING"

        job["retries"] = 0

        job["last_error"] = ""

        job["failed_at"] = 0

        job["run_at"] = time.time() + 5

        r.zadd(
            "jobs",
            {
                json.dumps(job): job["run_at"]
            }
        )

        r.hset(
            "job_details",
            job_id,
            json.dumps(job)
        )

        return True
    
    def move_to_dlq(self, job):

        r.hset(
            "dead_letter_jobs",
            job.id,
            json.dumps(job.__dict__)
        )
    
    def get_dead_letter_jobs(self):

        jobs = []

        for _, job_json in r.hgetall(
            "dead_letter_jobs"
        ).items():

            jobs.append(
                json.loads(job_json)
            )

        return jobs
