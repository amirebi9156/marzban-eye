from fastapi import APIRouter, Depends
from app.services.marzban_client import marzban
from app.core.auth import get_current_user

router = APIRouter(prefix="/inbounds", tags=["inbounds"])

@router.get("", dependencies=[Depends(get_current_user)])
def list_inbounds():
    return marzban.list_inbounds()
