from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class VideoFeedback(Base):
    __tablename__ = "video_feedback"
    __table_args__ = (
        UniqueConstraint("completed_video_id", "reviewer_id", name="uq_video_feedback_video_reviewer"),
    )

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    completed_video_id: Mapped[int] = mapped_column(ForeignKey("completed_videos.id"), nullable=False)
    reviewer_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    feedback_text: Mapped[str] = mapped_column(Text, nullable=False)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
