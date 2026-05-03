import asyncio
from worker.worker import run_worker

if __name__ == "__main__":
    print("Starting Worker...")
    asyncio.run(run_worker())