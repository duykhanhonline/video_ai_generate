from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.core.database import get_db
from app.models.asset import Asset
from app.schemas.asset import AssetRead
from app.core.security import hash_password

router = APIRouter(prefix="/api/tiny", tags=["tiny"])

@router.get("/hash")
def get_hash(password:str)-> dict:

    return {'password':password,
    'hash':hash_password(password)
    }
	