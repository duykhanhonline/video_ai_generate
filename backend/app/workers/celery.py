import os

from celery import Celery

redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "ambient_video",
    broker=redis_url,
    backend=redis_url,
)


@celery_app.task
def ping() -> str:
    return "pong"
