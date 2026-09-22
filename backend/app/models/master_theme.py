from datetime import datetime

from sqlalchemy import JSON, DateTime, Integer, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column

from app.core.database import Base


class MasterTheme(Base):
    __tablename__ = "master_themes"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    concept: Mapped[str] = mapped_column(Text, nullable=False)

    character_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    environment_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    visual_style_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    animation_rules_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)
    music_style_json: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    reference_image: Mapped[str | None] = mapped_column(String(500), nullable=True)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now()
    )
