
from fastapi import FastAPI

app = FastAPI(
    title="Healthchecks Alerts Service",
    version="1.0.0"
)


@app.get("/healthz")
def health_check():
    return {"status": "ok"}
