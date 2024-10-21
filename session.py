import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlmodel import Session, SQLModel


def get_session():
    with Session(engine) as session:
        yield session


load_dotenv()
engine = create_engine(os.getenv("DATABASE_URL") or "sqlite:///notes.db")
SQLModel.metadata.create_all(engine)

google_client_id = "636831366987-34qnitude6pg8d73u1njubuu05c8lo8o.apps.googleusercontent.com"
