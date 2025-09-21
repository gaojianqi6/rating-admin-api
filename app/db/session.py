from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("ADMIN_DATABASE_URL", "postgresql+psycopg://username:password@localhost/db_name")

# Ensure we're using psycopg3 by explicitly importing it
try:
    import psycopg
    print(f"Using psycopg version: {psycopg.__version__}")
    
    # If the URL uses postgresql:// format, convert it to postgresql+psycopg://
    if DATABASE_URL.startswith("postgresql://") and "+psycopg" not in DATABASE_URL:
        DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+psycopg://", 1)
        print(f"Converted URL to use psycopg dialect: {DATABASE_URL[:50]}...")
        
except ImportError:
    print("psycopg not available, falling back to default")

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
