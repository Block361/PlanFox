from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field
from app.models import ArtikelZustand, JobStatus


# ──────────────────────────────────────────────
# Kategorie
# ──────────────────────────────────────────────
class KategorieCreate(BaseModel):
    name: str = Field(..., max_length=100)
    beschreibung: Optional[str] = None


class KategorieOut(KategorieCreate):
    id: int
    erstellt_am: datetime

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Artikel
# ──────────────────────────────────────────────
class ArtikelCreate(BaseModel):
    name: str = Field(..., max_length=200)
    seriennummer: Optional[str] = None
    beschreibung: Optional[str] = None
    menge_gesamt: int = Field(1, ge=1)
    menge_verfuegbar: Optional[int] = None
    zustand: ArtikelZustand = ArtikelZustand.gut
    lagerort: Optional[str] = None
    anschaffungswert: Optional[float] = None
    kategorie_id: Optional[int] = None


class ArtikelUpdate(BaseModel):
    name: Optional[str] = None
    seriennummer: Optional[str] = None
    beschreibung: Optional[str] = None
    menge_gesamt: Optional[int] = Field(None, ge=1)
    menge_verfuegbar: Optional[int] = None
    zustand: Optional[ArtikelZustand] = None
    lagerort: Optional[str] = None
    anschaffungswert: Optional[float] = None
    kategorie_id: Optional[int] = None


class ArtikelOut(BaseModel):
    id: int
    name: str
    seriennummer: Optional[str]
    beschreibung: Optional[str]
    menge_gesamt: int
    menge_verfuegbar: int
    zustand: ArtikelZustand
    lagerort: Optional[str]
    anschaffungswert: Optional[float]
    kategorie: Optional[KategorieOut]
    erstellt_am: datetime
    aktualisiert_am: datetime

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Ausleihe
# ──────────────────────────────────────────────
class AusleiheCreate(BaseModel):
    artikel_id: int
    job_id: Optional[int] = None
    entleiher_name: str = Field(..., max_length=200)
    entleiher_kontakt: Optional[str] = None
    menge: int = Field(1, ge=1)
    rueckgabe_geplant: Optional[datetime] = None
    notizen: Optional[str] = None


class AusleiheOut(BaseModel):
    id: int
    artikel_id: int
    job_id: Optional[int]
    entleiher_name: str
    entleiher_kontakt: Optional[str]
    menge: int
    ausgeliehen_am: datetime
    rueckgabe_geplant: Optional[datetime]
    zurueckgegeben_am: Optional[datetime]
    notizen: Optional[str]
    ist_aktiv: bool

    model_config = {"from_attributes": True}


# ──────────────────────────────────────────────
# Job
# ──────────────────────────────────────────────
class JobCreate(BaseModel):
    name: str = Field(..., max_length=200)
    beschreibung: Optional[str] = None
    veranstaltungsort: Optional[str] = None
    beginn: Optional[datetime] = None
    ende: Optional[datetime] = None
    status: JobStatus = JobStatus.geplant
    kunde: Optional[str] = None
    notizen: Optional[str] = None


class JobUpdate(BaseModel):
    name: Optional[str] = None
    beschreibung: Optional[str] = None
    veranstaltungsort: Optional[str] = None
    beginn: Optional[datetime] = None
    ende: Optional[datetime] = None
    status: Optional[JobStatus] = None
    kunde: Optional[str] = None
    notizen: Optional[str] = None


class JobOut(BaseModel):
    id: int
    name: str
    beschreibung: Optional[str]
    veranstaltungsort: Optional[str]
    beginn: Optional[datetime]
    ende: Optional[datetime]
    status: JobStatus
    kunde: Optional[str]
    notizen: Optional[str]
    erstellt_am: datetime

    model_config = {"from_attributes": True}
