from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class CompletedVideo(Base):
    __tablename__ = "completed_videos"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    clip_id: Mapped[int] = mapped_column(ForeignKey("clips.id"), nullable=False)
    asset_id: Mapped[int] = mapped_column(ForeignKey("assets.id"), nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
