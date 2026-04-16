"""
Helper script - creates the 'safeguard_db' PostgreSQL database if it doesn't exist,
then creates all tables defined in models.py via SQLAlchemy.
Run once: python create_db.py
"""
import os
import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT
from dotenv import load_dotenv

load_dotenv()

DB_USER     = os.getenv("DB_USER", "postgres")
DB_PASSWORD = os.getenv("DB_PASSWORD", "")
DB_HOST     = os.getenv("DB_HOST", "localhost")
DB_PORT     = os.getenv("DB_PORT", "5432")
DB_NAME     = os.getenv("DB_NAME", "safeguard_db")

# Step 1: Create the database if missing
print(f"[1/2] Connecting to PostgreSQL as '{DB_USER}' on {DB_HOST}:{DB_PORT} ...")

try:
    conn = psycopg2.connect(
        dbname="postgres",
        user=DB_USER,
        password=DB_PASSWORD,
        host=DB_HOST,
        port=int(DB_PORT),
    )
except psycopg2.OperationalError as e:
    print(f"\n[ERROR] Could not connect to PostgreSQL: {e}")
    print("\nPlease check your .env file:")
    print(f"  DB_USER     = {DB_USER}")
    print(f"  DB_PASSWORD = {'*' * len(DB_PASSWORD)}")
    print(f"  DB_HOST     = {DB_HOST}")
    print(f"  DB_PORT     = {DB_PORT}")
    raise SystemExit(1)

conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
cur = conn.cursor()

cur.execute(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
if cur.fetchone():
    print(f"    Database '{DB_NAME}' already exists - skipping creation.")
else:
    cur.execute(f"CREATE DATABASE {DB_NAME}")
    print(f"    Database '{DB_NAME}' created successfully.")

cur.close()
conn.close()

# Step 2: Create all tables
print(f"[2/2] Creating tables inside '{DB_NAME}' ...")

from database import engine, Base
import models  # noqa: F401 - registers models with Base

Base.metadata.create_all(bind=engine)
print("    All tables created successfully.")
print("\n[DONE] Setup complete. Start the server with:")
print("    uvicorn main:app --reload")
