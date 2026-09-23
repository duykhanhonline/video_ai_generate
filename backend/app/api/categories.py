from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.category import Category
from app.models.project import Project
from app.schemas.category import CategoryCreate, CategoryRead

router = APIRouter(prefix="/api/categories", tags=["categories"])


@router.post("", response_model=CategoryRead, status_code=201)
def create_category(payload: CategoryCreate, db: Session = Depends(get_db)) -> Category:
    existing = db.scalars(select(Category).where(Category.name == payload.name)).first()
    if existing is not None:
        raise HTTPException(status_code=409, detail="A category with this name already exists")

    category = Category(name=payload.name)
    db.add(category)
    db.commit()
    db.refresh(category)
    return category


@router.get("", response_model=list[CategoryRead])
def list_categories(db: Session = Depends(get_db)) -> list[Category]:
    return list(db.scalars(select(Category).order_by(Category.name)).all())


@router.delete("/{category_id}", status_code=204)
def delete_category(category_id: int, db: Session = Depends(get_db)) -> None:
    category = db.get(Category, category_id)
    if category is None:
        raise HTTPException(status_code=404, detail="Category not found")

    # Projects using this category keep existing (category is optional), they
    # just lose the reference rather than being blocked or deleted.
    projects = db.scalars(select(Project).where(Project.category_id == category_id)).all()
    for project in projects:
        project.category_id = None

    db.delete(category)
    db.commit()
