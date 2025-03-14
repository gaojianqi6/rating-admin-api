from sqlmodel import create_engine, Session
import os
from dotenv import load_dotenv

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+psycopg2://postgres:jerome.gao@localhost/rating_admin")

engine = create_engine(DATABASE_URL, echo=True)

def get_session():
    with Session(engine) as session:
        yield session
