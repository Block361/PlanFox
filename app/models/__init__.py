from datetime import datetime, date
from sqlalchemy import (
    Column, Integer, String, Text, Float, Boolean,
    DateTime, Date, ForeignKey, Enum as SAEnum
)
from sqlalchemy.orm import relationship, DeclarativeBase
import enum


class Base(DeclarativeBase):
    pass


class ArtikelZustand(str, enum.Enum):
    gut = "gut"
    beschaedigt = "beschaedigt"
    reparatur = "reparatur"
    ausgemustert = "ausgemustert"


class JobStatus(str, enum.Enum):
    geplant = "geplant"
    aktiv = "aktiv"
    abgeschlossen = "abgeschlossen"
    storniert = "storniert"


class Kategorie(Base):
    __tablename__ = "kategorien"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), unique=True, nullable=False)
    beschreibung = Column(Text, nullable=True)
    erstellt_am = Column(DateTime, default=datetime.utcnow)
    artikel = relationship("Artikel", back_populates="kategorie")


class Artikel(Base):
    __tablename__ = "artikel"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    seriennummer = Column(String(100), unique=True, nullable=True)
    beschreibung = Column(Text, nullable=True)
    menge_gesamt = Column(Integer, default=1, nullable=False)
    menge_verfuegbar = Column(Integer, default=1, nullable=False)
    zustand = Column(SAEnum(ArtikelZustand), default=ArtikelZustand.gut)
    lagerort = Column(String(200), nullable=True)
    anschaffungswert = Column(Float, nullable=True)
    kategorie_id = Column(Integer, ForeignKey("kategorien.id"), nullable=True)

    # ── Technische Attribute ──────────────────────
    laenge_m = Column(Float, nullable=True)                  # Länge in Metern
    stecker_a = Column(String(100), nullable=True)           # z.B. "XLR-M", "Schuko", "Speakon 4-pol"
    stecker_b = Column(String(100), nullable=True)           # z.B. "XLR-F", "Kaltgeräte", "Klinke 6,3mm"
    ist_adapter = Column(Boolean, default=False)             # True wenn A ≠ B
    leistung_w = Column(Float, nullable=True)                # Watt
    spannung_v = Column(Float, nullable=True)                # Volt
    impedanz_ohm = Column(Float, nullable=True)              # Ohm
    kabeltyp = Column(String(100), nullable=True)            # z.B. "symmetrisch", "digital", "Multicore"
    anzahl_kanaele = Column(Integer, nullable=True)          # für Multicore / Stagebox
    schutzklasse_ip = Column(String(20), nullable=True)      # z.B. "IP65"
    gewicht_kg = Column(Float, nullable=True)                # kg

    # ── Hersteller & Verwaltung ───────────────────
    hersteller = Column(String(200), nullable=True)
    modell = Column(String(200), nullable=True)
    farbe = Column(String(100), nullable=True)               # z.B. "schwarz", "rot (Rücklauf)"
    kaufdatum = Column(Date, nullable=True)
    garantie_bis = Column(Date, nullable=True)
    wartungshinweis = Column(Text, nullable=True)
    externe_id = Column(String(100), nullable=True, index=True)  # Import-ID aus externer Quelle

    erstellt_am = Column(DateTime, default=datetime.utcnow)
    aktualisiert_am = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    kategorie = relationship("Kategorie", back_populates="artikel")
    ausleihen = relationship("Ausleihe", back_populates="artikel")
    einheiten = relationship("ArtikelEinheit", back_populates="artikel", cascade="all, delete-orphan")


class Ausleihe(Base):
    __tablename__ = "ausleihen"
    id = Column(Integer, primary_key=True, index=True)
    artikel_id = Column(Integer, ForeignKey("artikel.id"), nullable=True)
    job_id = Column(Integer, ForeignKey("jobs.id"), nullable=True)
    entleiher_name = Column(String(200), nullable=False)
    entleiher_kontakt = Column(String(200), nullable=True)
    menge = Column(Integer, default=1, nullable=False)
    ausgeliehen_am = Column(DateTime, default=datetime.utcnow)
    rueckgabe_geplant = Column(DateTime, nullable=True)
    zurueckgegeben_am = Column(DateTime, nullable=True)
    notizen = Column(Text, nullable=True)
    ist_aktiv = Column(Boolean, default=True)
    artikel = relationship("Artikel", back_populates="ausleihen")
    job = relationship("Job", back_populates="ausleihen")


class Job(Base):
    __tablename__ = "jobs"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(200), nullable=False)
    beschreibung = Column(Text, nullable=True)
    veranstaltungsort = Column(String(300), nullable=True)
    beginn = Column(DateTime, nullable=True)
    ende = Column(DateTime, nullable=True)
    status = Column(SAEnum(JobStatus), default=JobStatus.geplant)
    kunde = Column(String(200), nullable=True)
    notizen = Column(Text, nullable=True)
    erstellt_am = Column(DateTime, default=datetime.utcnow)
    aktualisiert_am = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    ausleihen = relationship("Ausleihe", back_populates="job")


class ArtikelEinheit(Base):
    __tablename__ = "artikel_einheiten"
    id = Column(Integer, primary_key=True, index=True)
    artikel_id = Column(Integer, ForeignKey("artikel.id"), nullable=False)
    seriennummer = Column(String(100), unique=True, nullable=False, index=True)
    zustand = Column(SAEnum(ArtikelZustand), default=ArtikelZustand.gut)
    notizen = Column(Text, nullable=True)
    erstellt_am = Column(DateTime, default=datetime.utcnow)
    artikel = relationship("Artikel", back_populates="einheiten")