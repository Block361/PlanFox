from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.config import settings
from app.models import Base

engine = create_engine(settings.database_url, echo=settings.debug)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    """FastAPI dependency – liefert eine DB-Session und schließt sie danach."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables():
    """Erstellt alle Tabellen (nur für Entwicklung – produktiv Alembic nutzen)."""
    Base.metadata.create_all(bind=engine)
