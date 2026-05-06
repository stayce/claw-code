from pathlib import Path
from sqlmodel import SQLModel, Session, create_engine

DB_PATH = Path(__file__).parent / "todos.db"
engine = create_engine(f"sqlite:///{DB_PATH}", connect_args={"check_same_thread": False})


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def get_session():
    with Session(engine) as session:
        yield session
