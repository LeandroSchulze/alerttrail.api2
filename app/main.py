from pathlib import Path
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
import os

app = FastAPI(title="AlertTrail")

BASE_DIR = Path(__file__).resolve().parent.parent
CANDIDATES = [BASE_DIR / "templates", BASE_DIR / "app" / "templates"]
TEMPLATES_DIR = next((p for p in CANDIDATES if p.exists()), None)

# Static opcional
if (BASE_DIR / "static").is_dir():
    app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

templates = Jinja2Templates(directory=str(TEMPLATES_DIR)) if TEMPLATES_DIR else None

@app.get("/health")
def health():
    return {"status": "ok"}

@app.get("/", response_class=HTMLResponse)
def root(request: Request):
    if templates and (TEMPLATES_DIR / "index.html").exists():
        return templates.TemplateResponse("index.html", {"request": request, "title": "AlertTrail"})
    return RedirectResponse("/docs", status_code=307)
