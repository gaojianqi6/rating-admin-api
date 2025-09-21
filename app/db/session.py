from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("ADMIN_DATABASE_URL", "postgresql+psycopg://username:password@localhost/db_name")

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
