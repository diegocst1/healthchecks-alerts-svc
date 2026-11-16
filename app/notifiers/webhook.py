
import httpx


async def send_webhook(
    method: str,
    url: str,
    headers: dict[str, str] | None = None,
    body: str | None = None,
) -> None:
    """Enviar una notificación HTTP a un Webhook."""

    method = method.upper()

    if method not in ("GET", "POST", "PUT"):
        raise ValueError("Método HTTP no permitido")

    if not url.startswith(("http://", "https://")):
        raise ValueError("La URL debe utilizar HTTP o HTTPS")

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.request(
            method=method,
            url=url,
            headers=headers or {},
            content=body if method in ("POST", "PUT") else None,
        )

        response.raise_for_status()

