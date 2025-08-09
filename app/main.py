from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from app.api.v1 import auth, users, inbounds, stats

app = FastAPI(title="Marzban Eye", version="0.3.0")

templates = Jinja2Templates(directory="templates")

@app.get("/health")
def health_check():
    return {"ok": True}

# API routers
app.include_router(auth.router)
app.include_router(users.router)
app.include_router(inbounds.router)
app.include_router(stats.router)

# Pages
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.get("/dashboard", response_class=HTMLResponse)
def dashboard_page(request: Request):
    # توجه: خودِ داده‌ها با JWT محافظت می‌شوند؛ این صفحه فقط HTML می‌دهد.
    # اگر خواستی حتماً توکن داشته باشد، می‌توانیم هدر Authorization را بررسی کنیم (پیشرفته‌تر).
    return templates.TemplateResponse("dashboard.html", {"request": request})
