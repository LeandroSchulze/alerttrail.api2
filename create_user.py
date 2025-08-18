#!/usr/bin/env python3
"""Create or update users in AlertTrail (SQLite)."""
import argparse, getpass, sys
from app.main import SessionLocal, User, pwd_context

PLANS = {"free", "pro"}
ROLES = {"user", "admin"}

def parse_args():
    ap = argparse.ArgumentParser(description="Create or update an AlertTrail user (SQLite)")
    ap.add_argument("--email", required=True, help="User email")
    ap.add_argument("--password", help="User password (if omitted, you'll be prompted)")
    ap.add_argument("--plan", default="pro", choices=sorted(PLANS), help="Plan to assign (default: pro)")
    ap.add_argument("--role", default="user", choices=sorted(ROLES), help="Role to assign (default: user)")
    ap.add_argument("--update", action="store_true", help="Update existing user instead of failing")
    return ap.parse_args()

def main():
    args = parse_args()
    db = SessionLocal()
    try:
        email = args.email.strip().lower()
        if not args.password:
            args.password = getpass.getpass("Password: ")
        if len(args.password) < 8:
            print("[ERR] Password must be at least 8 characters.", file=sys.stderr); sys.exit(2)
        existing = db.query(User).filter(User.email == email).first()
        if existing and not args.update:
            print(f"[ERR] User {email} already exists. Use --update to modify.", file=sys.stderr); sys.exit(1)
        if existing:
            changed = []
            existing.hashed_password = pwd_context.hash(args.password); changed.append("password")
            if existing.plan != args.plan: existing.plan = args.plan; changed.append("plan")
            if existing.role != args.role: existing.role = args.role; changed.append("role")
            db.add(existing); db.commit()
            print(f"[OK] Updated {email} (" + ", ".join(changed or ["no changes"]) + ")")
        else:
            u = User(email=email, hashed_password=pwd_context.hash(args.password), plan=args.plan, role=args.role)
            db.add(u); db.commit()
            print(f"[OK] Created {email} (plan={args.plan}, role={args.role})")
    finally:
        db.close()

if __name__ == "__main__":
    main()
