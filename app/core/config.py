from pydantic import BaseModel
from dotenv import load_dotenv
import os

load_dotenv()

class Settings(BaseModel):
    MARZBAN_API_URL: str = os.getenv("MARZBAN_API_URL", "")
    MARZBAN_API_KEY: str = os.getenv("MARZBAN_API_KEY", "")
    PANEL_API_KEY: str = os.getenv("PANEL_API_KEY", "")
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    APP_PORT: int = int(os.getenv("APP_PORT", "9000"))

settings = Settings()
