# app/services/marzban_client.py
import os
import httpx

class MarzbanClient:
    def __init__(self):
        # Base URL
        self.base_url = (os.getenv("MARZBAN_API_URL", "") or "").strip().rstrip("/")

        # Token precedence: first MARZBAN_API_TOKEN, then MARZBAN_API_KEY
        self.token = (
            os.getenv("MARZBAN_API_TOKEN")
            or os.getenv("MARZBAN_API_KEY")
            or ""
        ).strip()

        # SSL verification (default: True)
        self.verify_ssl = (os.getenv("VERIFY_SSL", "True").strip().lower() == "true")

        # Optional timeout via env (default 15s)
        timeout_env = os.getenv("MARZBAN_TIMEOUT", "").strip()
        try:
            self.timeout = float(timeout_env) if timeout_env else 15.0
        except ValueError:
            self.timeout = 15.0

        # Validations with clear messages
        if not self.base_url:
            raise RuntimeError("MARZBAN_API_URL is not set in .env")
        if not self.token:
            raise RuntimeError("Neither MARZBAN_API_TOKEN nor MARZBAN_API_KEY is set in .env")

        # HTTP client and headers
        self.headers = {"Authorization": f"Bearer {self.token}"}
        self.client = httpx.Client(verify=self.verify_ssl, timeout=self.timeout)

    def _url(self, path: str) -> str:
        return f"{self.base_url}{path}"

    def list_inbounds(self):
        resp = self.client.get(self._url("/api/inbounds"), headers=self.headers)
        resp.raise_for_status()
        return resp.json()

    def list_users(self, limit: int = 100, offset: int = 0):
        resp = self.client.get(
            self._url(f"/api/users?limit={limit}&offset={offset}"),
            headers=self.headers,
        )
        resp.raise_for_status()
        return resp.json()

    def close(self):
        try:
            self.client.close()
        except Exception:
            pass

    def __del__(self):
        self.close()


# Singleton instance (keeps behavior compatible with previous code)
marzban = MarzbanClient()
