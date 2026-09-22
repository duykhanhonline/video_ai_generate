import os

from celery import Celery

from app.core.logging import configure_logging

configure_logging("worker.log")

redis_url = os.environ.get("REDIS_URL", "redis://redis:6379/0")

celery_app = Celery(
    "ambient_video",
    broker=redis_url,
    backend=redis_url,
    include=["app.workers.image_tasks"],
)

# Celery hijacks the root logger by default, stripping any handlers configured
# before startup (including our rotating file handler). Disable that so
# configure_logging()'s file handler actually receives worker log output.
celery_app.conf.worker_hijack_root_logger = False


@celery_app.task
def ping() -> str:
    return "pong"
