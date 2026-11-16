
import asyncio
import json
import logging
import os

import aio_pika

logger = logging.getLogger(__name__)

QUEUE_NAME = "healthchecks.alerts"


async def process_message(message: aio_pika.IncomingMessage):
    async with message.process(requeue=True):
        event = json.loads(message.body.decode())

        logger.info(
            "Evento recibido: %s",
            event
        )


async def consume_alerts():
    password = os.environ["RABBITMQ_PASSWORD"]

    connection = await aio_pika.connect_robust(
        host="127.0.0.1",
        port=5672,
        login="alerts",
        password=password,
    )

    async with connection:
        channel = await connection.channel()

        await channel.set_qos(prefetch_count=1)

        queue = await channel.declare_queue(
            QUEUE_NAME,
            durable=True,
        )

        logger.info(
            "Esperando eventos en %s",
            QUEUE_NAME
        )

        await queue.consume(process_message)

        await asyncio.Future()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(consume_alerts())
