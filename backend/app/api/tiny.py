from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.asset import Asset
from app.schemas.asset import AssetRead

router = APIRouter(prefix="/api/tiny", tags=["tiny"])

@router.get("/hash",password:str)
def get_hash()-> dict:

    return {'password':password}
	