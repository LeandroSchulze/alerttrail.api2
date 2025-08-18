#!/usr/bin/env python3
"""
Import users in bulk from a CSV file.
CSV columns: email,password,plan,role
- plan defaults to 'pro' if missing
- role defaults to 'user' if missing
- --update allows updating existing users
Usage:
  python import_users_csv.py users.csv --update
"""
import csv, sys, argparse
from app.main import SessionLocal, User, pwd_context

PLANS = {"free", "pro"}
ROLES = {"user", "admin"}

def parse_args():
    ap = argparse.ArgumentParser()
    ap.add_argument("csv_path", help="Path to CSV file")
    ap.add_argument("--update", action="store_true", help="Update existing users")
    return ap.parse_args()

def main():
    args = parse_args()
    db = SessionLocal()
    created = updated = skipped = 0
    try:
        with open(args.csv_path, newline="", encoding="utf-8") as fh:
            reader = csv.DictReader(fh)
            for i, row in enumerate(reader, start=1):
                email = (row.get("email") or "").strip().lower()
                password = (row.get("password") or "").strip()
                plan = (row.get("plan") or "pro").strip().lower()
                role = (row.get("role") or "user").strip().lower()

                if not email or not password:
                    print(f"[row {i}] skip: missing email or password", file=sys.stderr); skipped += 1; continue
                if len(password) < 8:
                    print(f"[row {i}] skip: password too short (<8)", file=sys.stderr); skipped += 1; continue
                if plan not in PLANS:
                    print(f"[row {i}] skip: invalid plan '{plan}'", file=sys.stderr); skipped += 1; continue
                if role not in ROLES:
                    print(f"[row {i}] skip: invalid role '{role}'", file=sys.stderr); skipped += 1; continue

                existing = db.query(User).filter(User.email == email).first()
                if existing:
                    if not args.update:
                        print(f"[row {i}] skip: user exists ({email})", file=sys.stderr); skipped += 1; continue
                    changed = []
                    if password:
                        existing.hashed_password = pwd_context.hash(password); changed.append("password")
                    if existing.plan != plan:
                        existing.plan = plan; changed.append("plan")
                    if existing.role != role:
                        existing.role = role; changed.append("role")
                    db.add(existing); db.commit(); updated += 1
                else:
                    u = User(email=email, hashed_password=pwd_context.hash(password), plan=plan, role=role)
                    db.add(u); db.commit(); created += 1
        print(f"[OK] created={created}, updated={updated}, skipped={skipped}")
    finally:
        db.close()

if __name__ == "__main__":
    main()
