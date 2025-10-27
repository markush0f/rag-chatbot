from sqlmodel import SQLModel, create_engine, Session
from app.core.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    echo=False,  # SQL Logs
    pool_pre_ping=True, 
)


def init_db():
    SQLModel.metadata.create_all(engine)
    print("Tablas creadas o verificadas correctamente.")


def get_session():
    with Session(engine) as session:
        yield session
