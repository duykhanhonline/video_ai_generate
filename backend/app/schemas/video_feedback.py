from datetime import datetime

from pydantic import BaseModel, Field


class VideoFeedbackUpsert(BaseModel):
    feedback_text: str = Field(min_length=1)


class VideoFeedbackRead(BaseModel):
    id: int
    completed_video_id: int
    reviewer_id: int
    reviewer_name: str
    feedback_text: str
    created_at: datetime
    updated_at: datetime
