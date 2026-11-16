
import asyncio
import logging
import os

import aio_pika

from app.schemas import CheckDownEvent

logger = logging.getLogger(__name__)

QUEUE_NAME = "healthchecks.alerts"


async def process_message(message: aio_pika.IncomingMessage):
    async with message.process(requeue=True):
        event = CheckDownEvent.model_validate_json(message.body)

        logger.info(
            "Alerta recibida: check_id=%s, nombre=%s, estado=%s",
            event.payload.check_id,
            event.payload.check_name,
            event.payload.new_status,
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
            QUEUE_NAME,
        )

        await queue.consume(process_message)

        await asyncio.Future()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(consume_alerts())

