import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import Base
from app.services import artikel as artikel_svc
from app.schemas import ArtikelCreate, ArtikelUpdate

# In-memory SQLite für Tests
TEST_DATABASE_URL = "sqlite:///:memory:"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestSession = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture
def db():
    Base.metadata.create_all(bind=engine)
    session = TestSession()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


def test_artikel_erstellen(db):
    data = ArtikelCreate(name="XLR-Kabel 10m", menge_gesamt=20, lagerort="Regal A1")
    artikel = artikel_svc.create_artikel(db, data)
    assert artikel.id is not None
    assert artikel.name == "XLR-Kabel 10m"
    assert artikel.menge_verfuegbar == 20


def test_artikel_aktualisieren(db):
    data = ArtikelCreate(name="Lautsprecher", menge_gesamt=4)
    artikel = artikel_svc.create_artikel(db, data)
    aktualisiert = artikel_svc.update_artikel(db, artikel.id, ArtikelUpdate(lagerort="Keller B"))
    assert aktualisiert.lagerort == "Keller B"


def test_artikel_loeschen(db):
    data = ArtikelCreate(name="Stativ")
    artikel = artikel_svc.create_artikel(db, data)
    assert artikel_svc.delete_artikel(db, artikel.id) is True
    assert artikel_svc.get_artikel(db, artikel.id) is None


def test_artikel_suche(db):
    artikel_svc.create_artikel(db, ArtikelCreate(name="XLR-Kabel 5m"))
    artikel_svc.create_artikel(db, ArtikelCreate(name="DMX-Kabel"))
    artikel_svc.create_artikel(db, ArtikelCreate(name="Lautsprecher"))
    ergebnisse = artikel_svc.get_artikel_liste(db, suche="Kabel")
    assert len(ergebnisse) == 2
