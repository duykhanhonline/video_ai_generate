import asyncio
from datetime import UTC, datetime

from app.core.database import SessionLocal
from app.models.asset import Asset
from app.models.clip import Clip
from app.models.job import Job
from app.models.project import Project
from app.providers.registry import get_image_provider
from app.services.image_generation_service import ImageGenerationService
from app.services.storage_service import StorageService
from app.workers.celery import celery_app


@celery_app.task
def generate_clip_image_task(job_id: int, clip_id: int) -> None:
    asyncio.run(_generate_clip_image(job_id, clip_id))


async def _generate_clip_image(job_id: int, clip_id: int) -> None:
    db = SessionLocal()
    try:
        job = db.get(Job, job_id)
        clip = db.get(Clip, clip_id)
        if job is None or clip is None:
            return

        project = db.get(Project, clip.project_id)

        job.status = "RUNNING"
        job.started_at = datetime.now(UTC)
        db.commit()

        try:
            image_provider = get_image_provider(project.image_provider)
            service = ImageGenerationService(image_provider, StorageService())
            result = await service.generate_clip_image(project.id, clip_id, clip.image_prompt)

            asset = Asset(
                project_id=project.id,
                asset_type="generated_image",
                provider=result.provider,
                provider_model=result.provider_model,
                file_path=result.file_path,
                mime_type=result.mime_type,
            )
            db.add(asset)
            db.flush()

            clip.image_asset_id = asset.id
            clip.status = "image_generated"

            job.status = "COMPLETED"
            job.progress = 100
            job.completed_at = datetime.now(UTC)
            db.commit()
        except Exception as exc:
            job.status = "FAILED"
            job.error_message = str(exc)[:1000]
            job.completed_at = datetime.now(UTC)
            db.commit()
    finally:
        db.close()
