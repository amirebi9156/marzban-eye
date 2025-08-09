from fastapi import APIRouter, Depends, Query
from app.services.marzban_client import marzban
from app.core.auth import get_current_user

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", dependencies=[Depends(get_current_user)])
def list_users(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
    return marzban.list_users(limit=limit, offset=offset)
