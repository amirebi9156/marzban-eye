from fastapi import APIRouter, Depends, Query
from app.core.security import require_panel_api_key
from app.services.marzban_client import marzban

router = APIRouter(prefix="/users", tags=["users"])

@router.get("", dependencies=[Depends(require_panel_api_key)])
def list_users(limit: int = Query(100, ge=1, le=1000), offset: int = Query(0, ge=0)):
    return marzban.list_users(limit=limit, offset=offset)
