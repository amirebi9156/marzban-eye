from fastapi import FastAPI
from app.api.v1 import inbounds, users

app = FastAPI(title="Marzban Eye", version="0.1.0")

@app.get("/health")
def health_check():
    return {"ok": True}

app.include_router(inbounds.router)
app.include_router(users.router)
