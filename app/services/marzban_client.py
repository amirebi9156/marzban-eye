import httpx
from app.core.config import settings

class MarzbanClient:
    def __init__(self):
        self.base_url = settings.MARZBAN_API_URL.rstrip("/")
        self.headers = {"Authorization": f"Bearer {settings.MARZBAN_API_KEY}"}

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def list_inbounds(self):
        with httpx.Client(timeout=15.0, verify=True) as client:
            resp = client.get(self._url("/api/inbounds"), headers=self.headers)
            resp.raise_for_status()
            return resp.json()

    def list_users(self, limit: int = 100, offset: int = 0):
        with httpx.Client(timeout=15.0, verify=True) as client:
            resp = client.get(self._url(f"/api/users?limit={limit}&offset={offset}"), headers=self.headers)
            resp.raise_for_status()
            return resp.json()

marzban = MarzbanClient()
