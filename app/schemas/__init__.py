from datetime import datetime, date
from typing import Optional
from pydantic import BaseModel, Field
from app.models import ArtikelZustand, JobStatus


class KategorieCreate(BaseModel):
    name: str = Field(..., max_length=100)
    beschreibung: Optional[str] = None

class KategorieOut(KategorieCreate):
    id: int
    erstellt_am: datetime
    model_config = {"from_attributes": True}


# ── Artikel ──────────────────────────────────────────────────
_artikel_felder = dict(
    name=None, seriennummer=None, beschreibung=None,
    menge_gesamt=None, menge_verfuegbar=None,
    zustand=None, lagerort=None, anschaffungswert=None, kategorie_id=None,
    # Technisch
    laenge_m=None, stecker_a=None, stecker_b=None, ist_adapter=None,
    leistung_w=None, spannung_v=None, impedanz_ohm=None,
    kabeltyp=None, anzahl_kanaele=None, schutzklasse_ip=None, gewicht_kg=None,
    # Verwaltung
    hersteller=None, modell=None, farbe=None,
    kaufdatum=None, garantie_bis=None, wartungshinweis=None,
)

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
    # Technisch
    laenge_m: Optional[float] = None
    stecker_a: Optional[str] = None
    stecker_b: Optional[str] = None
    ist_adapter: bool = False
    leistung_w: Optional[float] = None
    spannung_v: Optional[float] = None
    impedanz_ohm: Optional[float] = None
    kabeltyp: Optional[str] = None
    anzahl_kanaele: Optional[int] = None
    schutzklasse_ip: Optional[str] = None
    gewicht_kg: Optional[float] = None
    # Verwaltung
    hersteller: Optional[str] = None
    modell: Optional[str] = None
    farbe: Optional[str] = None
    kaufdatum: Optional[date] = None
    garantie_bis: Optional[date] = None
    wartungshinweis: Optional[str] = None


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
    laenge_m: Optional[float] = None
    stecker_a: Optional[str] = None
    stecker_b: Optional[str] = None
    ist_adapter: Optional[bool] = None
    leistung_w: Optional[float] = None
    spannung_v: Optional[float] = None
    impedanz_ohm: Optional[float] = None
    kabeltyp: Optional[str] = None
    anzahl_kanaele: Optional[int] = None
    schutzklasse_ip: Optional[str] = None
    gewicht_kg: Optional[float] = None
    hersteller: Optional[str] = None
    modell: Optional[str] = None
    farbe: Optional[str] = None
    kaufdatum: Optional[date] = None
    garantie_bis: Optional[date] = None
    wartungshinweis: Optional[str] = None
    beschreibung: Optional[str] = None


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
    # Technisch
    laenge_m: Optional[float]
    stecker_a: Optional[str]
    stecker_b: Optional[str]
    ist_adapter: bool
    leistung_w: Optional[float]
    spannung_v: Optional[float]
    impedanz_ohm: Optional[float]
    kabeltyp: Optional[str]
    anzahl_kanaele: Optional[int]
    schutzklasse_ip: Optional[str]
    gewicht_kg: Optional[float]
    # Verwaltung
    hersteller: Optional[str]
    modell: Optional[str]
    farbe: Optional[str]
    kaufdatum: Optional[date]
    garantie_bis: Optional[date]
    wartungshinweis: Optional[str]
    erstellt_am: datetime
    aktualisiert_am: datetime
    model_config = {"from_attributes": True}


# ── Ausleihe ─────────────────────────────────────────────────
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
    artikel_id: Optional[int]
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


# ── Job ──────────────────────────────────────────────────────
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