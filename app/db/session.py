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
    
    # Handle schema parameter for psycopg3 - remove it from URL and set as connect_args
    connect_args = {}
    if "?schema=" in DATABASE_URL:
        # Extract schema from URL
        schema_part = DATABASE_URL.split("?schema=")[1]
        if "&" in schema_part:
            schema = schema_part.split("&")[0]
        else:
            schema = schema_part
        
        # Remove schema from URL
        DATABASE_URL = DATABASE_URL.split("?schema=")[0]
        if "&" in DATABASE_URL:
            DATABASE_URL = DATABASE_URL.split("&")[0]
        
        # Set schema in connect_args
        connect_args["options"] = f"-c search_path={schema}"
        print(f"Set schema '{schema}' via connect_args for psycopg3")
        
except ImportError:
    print("psycopg not available, falling back to default")
    connect_args = {}

engine = create_engine(DATABASE_URL, echo=True, connect_args=connect_args)

def get_session():
    with Session(engine) as session:
        yield session
