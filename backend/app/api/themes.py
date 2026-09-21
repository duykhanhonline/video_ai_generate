import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.master_theme import MasterTheme
from app.providers.registry import get_llm_provider
from app.schemas.ai_director import MasterThemeDraft, MasterThemeGenerateRequest
from app.schemas.master_theme import MasterThemeCreate, MasterThemeRead, MasterThemeUpdate
from app.services.director_service import AIDirectorService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/themes", tags=["themes"])


@router.post("/generate", response_model=MasterThemeDraft)
async def generate_master_theme(payload: MasterThemeGenerateRequest) -> MasterThemeDraft:
    try:
        director = AIDirectorService(llm_provider=get_llm_provider())
        return await director.generate_master_theme(payload.idea)
    except Exception:
        logger.exception("AI Director master theme generation failed")
        raise HTTPException(
            status_code=502, detail="AI Director generation failed. Check LLM provider configuration."
        ) from None


@router.post("", response_model=MasterThemeRead, status_code=201)
def create_theme(payload: MasterThemeCreate, db: Session = Depends(get_db)) -> MasterTheme:
    theme = MasterTheme(**payload.model_dump())
    db.add(theme)
    db.commit()
    db.refresh(theme)
    return theme


@router.get("", response_model=list[MasterThemeRead])
def list_themes(db: Session = Depends(get_db)) -> list[MasterTheme]:
    return list(db.scalars(select(MasterTheme)).all())


@router.get("/{theme_id}", response_model=MasterThemeRead)
def get_theme(theme_id: int, db: Session = Depends(get_db)) -> MasterTheme:
    theme = db.get(MasterTheme, theme_id)
    if theme is None:
        raise HTTPException(status_code=404, detail="Master theme not found")
    return theme


@router.patch("/{theme_id}", response_model=MasterThemeRead)
def update_theme(
    theme_id: int, payload: MasterThemeUpdate, db: Session = Depends(get_db)
) -> MasterTheme:
    theme = db.get(MasterTheme, theme_id)
    if theme is None:
        raise HTTPException(status_code=404, detail="Master theme not found")

    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(theme, field, value)

    db.commit()
    db.refresh(theme)
    return theme


@router.delete("/{theme_id}", status_code=204)
def delete_theme(theme_id: int, db: Session = Depends(get_db)) -> None:
    theme = db.get(MasterTheme, theme_id)
    if theme is None:
        raise HTTPException(status_code=404, detail="Master theme not found")
    db.delete(theme)
    db.commit()
