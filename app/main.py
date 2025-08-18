from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

try:
    from fastapi.templating import Jinja2Templates
except Exception:
    Jinja2Templates = None

app = FastAPI(title="AlertTrail")

# Import and include routers if present
try:
    from app.routers import profile, settings, admin
    app.include_router(profile.router)
    app.include_router(settings.router)
    app.include_router(admin.router)
except Exception as e:
    print(f"[routers] aviso: {e}")

# Static / templates (optional)
import os
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")
if Jinja2Templates:
    templates = Jinja2Templates(directory="templates")

@app.get("/health")
def health():
    return {"status": "ok"}