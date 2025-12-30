# database.py - UPDATED FOR RENDER.COM
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

def get_database_url():
    """Get database URL based on environment"""
    
    # 1. Check for Render PostgreSQL (if you upgrade to paid tier)
    if 'DATABASE_URL' in os.environ and 'postgresql' in os.environ['DATABASE_URL']:
        print("🔧 Using PostgreSQL on Render")
        return os.environ['DATABASE_URL']
    
    # 2. Check for PythonAnywhere
    elif 'PYTHONANYWHERE_DOMAIN' in os.environ:
        # PythonAnywhere: Use home directory for database
        home_dir = os.path.expanduser('~')
        db_path = os.path.join(home_dir, 'learnsphere.db')
        db_url = f"sqlite:///{db_path}"
        print(f"🔧 PythonAnywhere DB: {db_url}")
        return db_url
    
    # 3. Check for Render SQLite (free tier)
    elif 'RENDER' in os.environ:
        print("🔧 Using SQLite on Render (free tier)")
        # Use a persistent location
        return "sqlite:///./learnsphere.db"
    
    # 4. Local development
    else:
        print("🔧 Using Local SQLite DB")
        return "sqlite:///./learnsphere.db"

# Get database URL
DATABASE_URL = get_database_url()

# Create engine with SQLite compatibility
engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {},
    echo=False  # Set to True for debugging SQL queries
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()