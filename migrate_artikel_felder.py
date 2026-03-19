"""
Migrations-Script: Neue Artikel-Attribute hinzufügen.
Ausführen mit: docker compose exec api python migrate_artikel_felder.py
"""
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import engine
from sqlalchemy import text

NEUE_SPALTEN = [
    ("laenge_m",        "FLOAT"),
    ("stecker_a",       "VARCHAR(100)"),
    ("stecker_b",       "VARCHAR(100)"),
    ("ist_adapter",     "BOOLEAN DEFAULT FALSE"),
    ("leistung_w",      "FLOAT"),
    ("spannung_v",      "FLOAT"),
    ("impedanz_ohm",    "FLOAT"),
    ("kabeltyp",        "VARCHAR(100)"),
    ("anzahl_kanaele",  "INTEGER"),
    ("schutzklasse_ip", "VARCHAR(20)"),
    ("gewicht_kg",      "FLOAT"),
    ("hersteller",      "VARCHAR(200)"),
    ("modell",          "VARCHAR(200)"),
    ("farbe",           "VARCHAR(100)"),
    ("kaufdatum",       "DATE"),
    ("garantie_bis",    "DATE"),
    ("wartungshinweis", "TEXT"),
]

def spalte_existiert(conn, tabelle, spalte):
    result = conn.execute(text(
        "SELECT column_name FROM information_schema.columns "
        "WHERE table_name=:t AND column_name=:c"
    ), {"t": tabelle, "c": spalte})
    return result.fetchone() is not None

def migrate():
    with engine.connect() as conn:
        hinzugefuegt = 0
        uebersprungen = 0
        for spalte, typ in NEUE_SPALTEN:
            if spalte_existiert(conn, "artikel", spalte):
                print(f"  ⏭  {spalte} existiert bereits")
                uebersprungen += 1
            else:
                conn.execute(text(f"ALTER TABLE artikel ADD COLUMN {spalte} {typ}"))
                print(f"  ✓  {spalte} ({typ}) hinzugefügt")
                hinzugefuegt += 1
        conn.commit()
    print(f"\n{hinzugefuegt} Spalten hinzugefügt, {uebersprungen} übersprungen.")

if __name__ == "__main__":
    migrate()