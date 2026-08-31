"""
Database bootstrap script.
Creates tables, roles, and demo users.

Demo users are CLEARLY IDENTIFIED as development/demo accounts.
Credentials come from environment variables.
"""
import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.core.config import settings
from app.core.database import engine, AsyncSessionLocal
from app.core.security import hash_password
from app.models import *  # Import all models


DEMO_USERS = [
    {
        "email": os.getenv("ADMIN_EMAIL", "admin@procurex.local"),
        "username": "admin",
        "full_name": "System Administrator [DEMO]",
        "password": os.getenv("ADMIN_PASSWORD", "Admin@123!Demo"),
        "role": "ADMIN",
        "department": "IT Administration",
        "designation": "System Administrator",
        "employee_id": "DEMO-ADMIN-001",
    },
    {
        "email": os.getenv("OFFICER_EMAIL", "officer@procurex.local"),
        "username": "officer",
        "full_name": "Rajesh Kumar [DEMO Procurement Officer]",
        "password": os.getenv("OFFICER_PASSWORD", "Officer@123!Demo"),
        "role": "PROCUREMENT_OFFICER",
        "department": "Procurement Division",
        "designation": "Senior Procurement Officer",
        "employee_id": "DEMO-PO-001",
    },
    {
        "email": os.getenv("ANALYST_EMAIL", "analyst@procurex.local"),
        "username": "analyst",
        "full_name": "Priya Sharma [DEMO Analyst]",
        "password": os.getenv("ANALYST_PASSWORD", "Analyst@123!Demo"),
        "role": "ANALYST",
        "department": "Procurement Division",
        "designation": "Bid Analyst",
        "employee_id": "DEMO-AN-001",
    },
    {
        "email": os.getenv("AUDITOR_EMAIL", "auditor@procurex.local"),
        "username": "auditor",
        "full_name": "Suresh Patel [DEMO Auditor]",
        "password": os.getenv("AUDITOR_PASSWORD", "Auditor@123!Demo"),
        "role": "VIEWER",
        "department": "Internal Audit",
        "designation": "Internal Auditor",
        "employee_id": "DEMO-AU-001",
    },
]


async def create_tables():
    print("Creating database tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✓ Tables created")


async def seed_demo_users():
    from app.models.user import User
    from sqlalchemy import select

    print("\nSeeding demo users...")
    print("⚠️  WARNING: These are DEMO accounts — do not use in production!\n")

    async with AsyncSessionLocal() as db:
        for user_data in DEMO_USERS:
            result = await db.execute(select(User).where(User.email == user_data["email"]))
            existing = result.scalar_one_or_none()

            if existing:
                print(f"  ↳ [SKIP] {user_data['username']} ({user_data['email']}) — already exists")
                continue

            user = User(
                email=user_data["email"],
                username=user_data["username"],
                full_name=user_data["full_name"],
                hashed_password=hash_password(user_data["password"]),
                role=user_data["role"],
                department=user_data.get("department"),
                designation=user_data.get("designation"),
                employee_id=user_data.get("employee_id"),
                is_active=True,
                is_verified=True,
            )
            db.add(user)
            await db.commit()
            print(f"  ✓ Created: {user_data['username']} ({user_data['role']}) — {user_data['email']}")

    print("\nDemo Credentials:")
    print("─" * 60)
    for u in DEMO_USERS:
        print(f"  {u['role']:25} | {u['username']:12} | {u['password']}")
    print("─" * 60)
    print("⚠️  These are DEMO credentials. Change in production!\n")


async def create_minio_buckets():
    print("Creating MinIO buckets...")
    try:
        from minio import Minio
        client = Minio(
            settings.MINIO_ENDPOINT,
            access_key=settings.MINIO_ACCESS_KEY,
            secret_key=settings.MINIO_SECRET_KEY,
            secure=settings.MINIO_SECURE,
        )
        for bucket in [settings.MINIO_BUCKET_DOCUMENTS, settings.MINIO_BUCKET_DEMO]:
            if not client.bucket_exists(bucket):
                client.make_bucket(bucket)
                print(f"  ✓ Created bucket: {bucket}")
            else:
                print(f"  ↳ [SKIP] Bucket exists: {bucket}")
    except Exception as exc:
        print(f"  ⚠ MinIO not available: {exc}")
        print("  ↳ Bucket creation skipped (will retry on first upload)")


async def main():
    print("=" * 60)
    print("PROCUREX — Database Bootstrap")
    print("SIH26100 · AI-Powered Bid Compliance Verification")
    print("=" * 60)
    print(f"Environment: {settings.ENVIRONMENT}")
    print(f"Demo Mode: {settings.ENABLE_DEMO_MODE}")
    print(f"Database: {settings.DATABASE_URL.split('@')[-1]}")
    print()

    await create_tables()
    await seed_demo_users()
    await create_minio_buckets()

    print("\n✓ Bootstrap complete!")
    print("  Start the backend: uvicorn app.main:app --reload")
    print("  API docs: http://localhost:8000/api/docs")
    print()


if __name__ == "__main__":
    asyncio.run(main())
