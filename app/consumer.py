
import asyncio
import logging
import os

import aio_pika
from pydantic import ValidationError

from app.schemas import CheckDownEvent

logger = logging.getLogger(__name__)

QUEUE_NAME = "healthchecks.alerts"
DLQ_NAME = "healthchecks.alerts.dlq"


async def process_message(message: aio_pika.IncomingMessage):
    try:
        event = CheckDownEvent.model_validate_json(message.body)
    except ValidationError as exc:
        logger.warning(
            "Evento inválido enviado a DLQ: %s",
            exc,
        )
        await message.reject(requeue=False)
        return

    logger.info(
        "Alerta recibida: check_id=%s, nombre=%s, estado=%s",
        event.payload.check_id,
        event.payload.check_name,
        event.payload.new_status,
    )

    await message.ack()


async def consume_alerts():
    connection = await aio_pika.connect_robust(
        host="127.0.0.1",
        port=5672,
        login="alerts",
        password=os.environ["RABBITMQ_PASSWORD"],
    )

    async with connection:
        channel = await connection.channel()
        await channel.set_qos(prefetch_count=1)

        await channel.declare_queue(
            DLQ_NAME,
            durable=True,
        )

        queue = await channel.declare_queue(
            QUEUE_NAME,
            durable=True,
            arguments={
                "x-dead-letter-exchange": "",
                "x-dead-letter-routing-key": DLQ_NAME,
            },
        )

        logger.info("Esperando eventos en %s", QUEUE_NAME)

        await queue.consume(process_message)
        await asyncio.Future()


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    try:
        asyncio.run(consume_alerts())
    except KeyboardInterrupt:
        logger.info("Consumidor detenido")


