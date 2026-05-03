import redis
import json
import time

r = redis.Redis(host="localhost", port=6379, decode_responses=True)

class RedisStore:

    def add_job(self, job):
        r.zadd("jobs", {json.dumps(job.__dict__): job.run_at})

    def get_due_jobs(self):
        now = time.time()
        jobs = r.zrangebyscore("jobs", 0, now)

        if jobs:
            r.zremrangebyscore("jobs", 0, now)

        return jobs