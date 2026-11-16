
import asyncio
import unittest
from unittest.mock import patch

import httpx

from app.notifiers.webhook import send_webhook


class WebhookTests(unittest.TestCase):

    def test_webhook_post(self):
        requests = []

        def handler(request):
            requests.append(request)
            return httpx.Response(200)

        transport = httpx.MockTransport(handler)

        with patch(
            "app.notifiers.webhook.httpx.AsyncClient",
            return_value=httpx.AsyncClient(transport=transport),
        ):
            asyncio.run(
                send_webhook(
                    method="POST",
                    url="https://example.com/webhook",
                    headers={"Content-Type": "application/json"},
                    body='{"status": "down"}',
                )
            )

        self.assertEqual(len(requests), 1)
        self.assertEqual(requests[0].method, "POST")
        self.assertEqual(
            requests[0].content,
            b'{"status": "down"}',
        )

    def test_invalid_method(self):
        with self.assertRaises(ValueError):
            asyncio.run(
                send_webhook(
                    method="DELETE",
                    url="https://example.com/webhook",
                )
            )

    def test_invalid_url(self):
        with self.assertRaises(ValueError):
            asyncio.run(
                send_webhook(
                    method="POST",
                    url="ftp://example.com",
                )
            )


if __name__ == "__main__":
    unittest.main()
