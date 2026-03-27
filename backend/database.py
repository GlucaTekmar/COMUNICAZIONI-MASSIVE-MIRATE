import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.exc import OperationalError

# ==========================================
# DATABASE CONFIG
# ==========================================

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise Exception("DATABASE_URL non configurato")

# ==========================================
# ENGINE
# ==========================================

engine = create_engine(
    DATABASE_URL,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10
)

# ==========================================
# SESSION
# ==========================================

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

# ==========================================
# BASE
# ==========================================

Base = declarative_base()

# ==========================================
# CONNECTION CHECK
# ==========================================

def check_db_connection():
    try:
        conn = engine.connect()
        conn.close()
        return True
    except OperationalError:
        return False

# ==========================================
# DEPENDENCY (FastAPI)
# ==========================================

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
