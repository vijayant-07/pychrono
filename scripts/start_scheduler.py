import asyncio
from scheduler.scheduler import run_scheduler

if __name__ == "__main__":
    print("Starting Scheduler...")
    asyncio.run(run_scheduler())