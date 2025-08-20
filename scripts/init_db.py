# scripts/init_db.py
import os, sys
from sqlalchemy import inspect, text

# --- asegurar que el paquete app/ se pueda importar en Render ---
ROOT = os.path.dirname(os.path.dirname(__file__))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)

from app.database import Base, engine, SessionLocal
from app.models import User as UserModel

print(">> Creando tablas si no existen...")
Base.metadata.create_all(bind=engine)

# --- asegurar columnas 'role' y 'plan' (SQLite o Postgres) ---
insp = inspect(engine)
cols = {c["name"] for c in insp.get_columns("users")}
with engine.begin() as con:
    if "role" not in cols:
        con.execute(text("ALTER TABLE users ADD COLUMN role VARCHAR(50) DEFAULT 'user'"))
        print(">> Añadida columna users.role")
    else:
        print(">> Columna users.role ok")
    if "plan" not in cols:
        con.execute(text("ALTER TABLE users ADD COLUMN plan VARCHAR(50) DEFAULT 'free'"))
        print(">> Añadida columna users.plan")
    else:
        print(">> Columna users.plan ok")

# --- hash de password (bcrypt si está disponible) ---
try:
    import bcrypt
    def hash_pwd(p: str) -> str:
        return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
except Exception:
    def hash_pwd(p: str) -> str:
        return p

def ensure_user(db, email: str, password: str, name: str, role="user", plan="free"):
    u = db.query(UserModel).filter(UserModel.email == email).first()
    if not u:
        u = UserModel(email=email, name=name, hashed_password=hash_pwd(password))
        try:
            setattr(u, "role", role)
            setattr(u, "plan", plan)
        except Exception:
            pass
        db.add(u)
        db.commit()
        print(f">> Usuario creado: {email} (role={role}, plan={plan})")
        return
    # actualizar si falta info
    changed = False
    if not getattr(u, "name", None):
        u.name = name; changed = True
    try:
        if getattr(u, "role", None) is None:
            u.role = role; changed = True
        if getattr(u, "plan", None) is None:
            u.plan = plan; changed = True
    except Exception:
        pass
    if changed:
        db.commit()
        print(f">> Usuario actualizado: {email}")
    else:
        print(f">> Usuario ya existía: {email}")

db = SessionLocal()
try:
    # --- Admin ---
    ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@alerttrail.local")
    ADMIN_PASS  = os.getenv("ADMIN_PASS",  "admin123")
    ADMIN_NAME  = os.getenv("ADMIN_NAME",  "Admin")
    print(">> Asegurando admin:", ADMIN_EMAIL)
    ensure_user(db, ADMIN_EMAIL, ADMIN_PASS, ADMIN_NAME, role="admin", plan="pro")

    # --- Tester opcional ---
    TESTER_EMAIL = os.getenv("TESTER_EMAIL")
    TESTER_PASS  = os.getenv("TESTER_PASS")
    TESTER_NAME  = os.getenv("TESTER_NAME", "QA Tester")
    if TESTER_EMAIL and TESTER_PASS:
        print(">> Asegurando tester:", TESTER_EMAIL)
        ensure_user(db, TESTER_EMAIL, TESTER_PASS, TESTER_NAME, role="tester", plan="pro")
    else:
        print(">> TESTER_* no configurado; saltando usuario de prueba")
finally:
    db.close()

print("OK ✅")