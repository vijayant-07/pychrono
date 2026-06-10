import os
import asyncio

from dotenv import load_dotenv

from nats.aio.client import Client as NATS
from nats.js.api import StreamConfig

load_dotenv()


class NATSClient:

    def __init__(self):

        self.url = os.getenv(
            "NATS_URL",
            "nats://localhost:4222"
        )

        self.nc = NATS()
        self.js = None

    async def connect(self):

        while True:

            try:

                await self.nc.connect(
                    self.url
                )

                self.js = self.nc.jetstream()

                print(
                    f"Connected to NATS: {self.url}"
                )

                break

            except Exception as e:

                print(
                    f"NATS not ready: {e}"
                )

                await asyncio.sleep(5)

    async def setup_stream(self):

        try:

            await self.js.add_stream(
                name="TASKS",
                subjects=["tasks.execute"]
            )

        except Exception:
            pass

    async def publish(
        self,
        subject,
        data: bytes
    ):

        await self.js.publish(
            subject,
            data
        )

    async def subscribe(
        self,
        subject,
        durable
    ):

        return await self.js.subscribe(
            subject,
            durable=durable,
            manual_ack=True
        )