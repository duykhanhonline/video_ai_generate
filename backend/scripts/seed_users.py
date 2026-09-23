"""Seed a few initial users for local development.

Idempotent -- safe to run multiple times, skips any email that already
exists rather than erroring or duplicating.

Usage:
    docker compose exec backend python scripts/seed_users.py
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from app.core.database import SessionLocal  # noqa: E402
from app.core.security import hash_password  # noqa: E402
from app.models.user import User  # noqa: E402

SEED_USERS = [
    {"email": "contributor@example.com", "password": "changeme123", "role": "contributor"},
    {"email": "reviewer@example.com", "password": "changeme123", "role": "reviewer"},
]


def seed_users() -> None:
    db = SessionLocal()
    try:
        for entry in SEED_USERS:
            existing = db.query(User).filter(User.email == entry["email"]).first()
            if existing is not None:
                print(f"Skipping {entry['email']} (already exists)")
                continue

            db.add(
                User(
                    email=entry["email"],
                    password_hash=hash_password(entry["password"]),
                    role=entry["role"],
                )
            )
            print(f"Created {entry['email']} ({entry['role']})")

        db.commit()
    finally:
        db.close()


if __name__ == "__main__":
    seed_users()
    print("\nDefault password for all seeded users: changeme123")
    print("These are for local development only -- change or remove them before sharing access.")
