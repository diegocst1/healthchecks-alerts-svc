
import asyncio
import json
import os
from datetime import datetime, timezone
from uuid import uuid4

import aio_pika


async def main():
    connection = await aio_pika.connect_robust(
        host="127.0.0.1",
        port=5672,
        login="alerts",
        password=os.environ["RABBITMQ_PASSWORD"],
    )

    async with connection:
        channel = await connection.channel(
            publisher_confirms=True
        )

        event = {
            "event_id": str(uuid4()),
            "type": "healthchecks.check.down",
            "version": "1.0",
            "occurred_at": datetime.now(timezone.utc).isoformat(),
            "request_id": str(uuid4()),
            "payload": {
                "check_id": str(uuid4()),
                "check_name": "Servidor de prueba",
                "old_status": "up",
                "new_status": "down",
                "reason": "timeout",
            },
        }

        message = aio_pika.Message(
            body=json.dumps(event).encode("utf-8"),
            content_type="application/json",
            delivery_mode=aio_pika.DeliveryMode.PERSISTENT,
        )

        await channel.default_exchange.publish(
            message,
            routing_key="healthchecks.alerts",
            mandatory=True,
        )

        print("Evento de prueba publicado:")
        print(json.dumps(event, indent=2))


if __name__ == "__main__":
    asyncio.run(main())
