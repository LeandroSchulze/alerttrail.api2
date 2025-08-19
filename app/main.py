# app/main.py
from fastapi import FastAPI, Request
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
import os

app = FastAPI(title="AlertTrail")

# Templates (opcional)
try:
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="templates")
except Exception as e:
    templates = None
    print(f"[templates] aviso: {e}")

# Static (opcional)
if os.path.isdir("static"):
    app.mount("/static", StaticFiles(directory="static"), name="static")

def _include_safely(router_module, name):
    try:
        app.include_router(router_module.router)
        print(f"[routers] OK: {name}")
    except Exception as e:
        print(f"[routers] FALLÓ incluir {name}: {e}")

# Intenta importar routers desde app.routes (y como fallback app.routers)
# Ajustá los nombres a los que existan en tu repo (auth, users, dashboard, profile, settings, admin, etc.)
import importlib

for pkg in ("app.routes", "app.routers"):
    try:
        # ejemplo de módulos posibles: ajusta esta lista a tus archivos reales
        for mod in ("auth", "users", "dashboard", "profile", "settings", "admin"):
            try:
                m = importlib.import_module(f"{pkg}.{mod}")
                _include_safely(m, f"{pkg}.{mod}")
            except ModuleNotFoundError:
                # Es normal si no existe ese archivo; seguimos con el siguiente
                pass
    except Exception as e:
        print(f"[routers] aviso al importar desde {pkg}: {e}")

@app.get("/health")
def health():
    return {"status": "ok"}

# Página inicial -> redirige a /login si hay templates; sino devuelve JSON
@app.get("/", response_class=HTMLResponse)
def root():
    if templates and os.path.isfile(os.path.join("templates", "login.html")):
        return RedirectResponse(url="/login", status_code=307)
    return JSONResponse({"detail": "Root OK. No templates configured."})

# Página de login (HTML) si hay templates/login.html
@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if not templates:
        return JSONResponse({"detail": "Templates not configured"}, status_code=404)
    if not os.path.isfile(os.path.join("templates", "login.html")):
        return JSONResponse({"detail": "templates/login.html not found"}, status_code=404)
    return templates.TemplateResponse("login.html", {"request": request})
