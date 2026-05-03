import asyncio
from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig

class NATSClient:
    def __init__(self, url="nats://localhost:4222"):
        self.url = url
        self.nc = NATS()
        self.js = None

    async def connect(self):
        await self.nc.connect(self.url)
        self.js = self.nc.jetstream()

    async def setup_stream(self):
        await self.js.add_stream(
            name="TASKS",
            subjects=["tasks.execute"]
        )

    async def publish(self, subject, data: bytes):
        await self.js.publish(subject, data)

    async def subscribe(self, subject, durable):
        return await self.js.subscribe(
            subject,
            durable=durable,
            manual_ack=True
        )