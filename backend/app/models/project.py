from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class Project(Base):
    __tablename__ = "projects"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    master_theme_id: Mapped[int] = mapped_column(ForeignKey("master_themes.id"), nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    status: Mapped[str] = mapped_column(String(50), nullable=False, default="draft")

    clip_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    music_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    target_duration: Mapped[int] = mapped_column(Integer, nullable=False)

    image_provider: Mapped[str] = mapped_column(String(50), nullable=False, default="openai")
    video_provider: Mapped[str] = mapped_column(String(50), nullable=False, default="kling")
    music_provider: Mapped[str] = mapped_column(String(50), nullable=False, default="manual")
    owner_id: Mapped[int | None] = mapped_column(ForeignKey("users.id"), nullable=True)
    category_id: Mapped[int | None] = mapped_column(ForeignKey("categories.id"), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
