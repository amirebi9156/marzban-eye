from fastapi import APIRouter, Depends
from app.core.security import require_panel_api_key
from app.services.marzban_client import marzban

router = APIRouter(prefix="/inbounds", tags=["inbounds"])

@router.get("", dependencies=[Depends(require_panel_api_key)])
def list_inbounds():
    return marzban.list_inbounds()
