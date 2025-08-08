from fastapi import Header, HTTPException, status

from .config import settings

def require_panel_api_key(x_api_key: str | None = Header(default=None)):
    if not x_api_key or x_api_key != settings.PANEL_API_KEY:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid API key")
    return True
