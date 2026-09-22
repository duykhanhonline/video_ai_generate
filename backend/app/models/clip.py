from datetime import datetime

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Clip(Base):
    __tablename__ = "clips"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    project_id: Mapped[int] = mapped_column(ForeignKey("projects.id"), nullable=False)
    activity: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="pending")
    approved: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    image_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    image_asset_id: Mapped[int | None] = mapped_column(ForeignKey("assets.id"), nullable=True)
    video_prompt: Mapped[str | None] = mapped_column(Text, nullable=True)
    video_asset_id: Mapped[int | None] = mapped_column(ForeignKey("assets.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
