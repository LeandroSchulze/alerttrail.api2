# scripts/init_db.py
import os
from sqlalchemy import inspect, text

from app.database import Base, engine, SessionLocal
import app.models as models
from app.models import User as UserModel

print(">> Creando tablas si no existen (con modelos importados)...")
Base.metadata.create_all(bind=engine)

insp = inspect(engine)
tables = insp.get_table_names()
print(">> Tablas detectadas:", tables)
if "users" not in tables:
    Base.metadata.create_all(bind=engine)
    insp = inspect(engine)
    tables = insp.get_table_names()
    print(">> Tablas tras create_all:", tables)
    if "users" not in tables:
        raise RuntimeError("No se pudo crear la tabla 'users'.")

def has_column(conn, table: str, col: str) -> bool:
    rows = conn.execute(text(f"PRAGMA table_info({table});")).fetchall()
    return any(r[1] == col for r in rows)

with engine.begin() as conn:
    if not has_column(conn, "users", "role"):
        conn.execute(text("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user';"))
        print(">> Añadida columna users.role")
    else:
        print(">> Columna users.role ya existe")

    if not has_column(conn, "users", "plan"):
        conn.execute(text("ALTER TABLE users ADD COLUMN plan TEXT DEFAULT 'free';"))
        print(">> Añadida columna users.plan")
    else:
        print(">> Columna users.plan ya existe")

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@alerttrail.local")
ADMIN_PASS  = os.getenv("ADMIN_PASS",  "admin123")
ADMIN_NAME  = os.getenv("ADMIN_NAME",  "Admin")

try:
    import bcrypt
    def hash_pwd(p: str) -> str:
        return bcrypt.hashpw(p.encode(), bcrypt.gensalt()).decode()
except Exception:
    def hash_pwd(p: str) -> str:
        return p

print(">> Asegurando usuario admin:", ADMIN_EMAIL)
db = SessionLocal()
try:
    u = db.query(UserModel).filter(UserModel.email == ADMIN_EMAIL).first()
    if not u:
        admin = UserModel(
            email=ADMIN_EMAIL,
            name=ADMIN_NAME,
            hashed_password=hash_pwd(ADMIN_PASS),
        )
        db.add(admin)
        db.commit()
        db.refresh(admin)
        try:
            setattr(admin, "role", "admin")
            setattr(admin, "plan", "pro")
            db.commit()
            print(">> Admin creado con role=admin, plan=pro")
        except Exception:
            print(">> Admin creado (modelo sin campos role/plan)")
    else:
        changed = False
        if not getattr(u, "name", None):
            u.name = ADMIN_NAME; changed = True
        try:
            if getattr(u, "role", None) != "admin":
                u.role = "admin"; changed = True
            if getattr(u, "plan", None) != "pro":
                u.plan = "pro";   changed = True
        except Exception:
            pass
        if changed:
            db.commit(); print(">> Admin actualizado")
        else:
            print(">> Admin ya existía")
finally:
    db.close()

print("OK ✅")