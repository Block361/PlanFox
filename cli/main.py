"""
CLI-Tool für das Veranstaltungstechnik-Inventarsystem.
Verwendung: python -m cli.main --help
"""
import sys
import os

# Projektwurzel an den Anfang – überschreibt jedes fremde 'app'-Package
_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _root)

import click
from sqlalchemy.orm import Session
from app.database import SessionLocal, create_tables
from app.models import Artikel, Ausleihe, Job, ArtikelZustand
from app.schemas import ArtikelCreate, AusleiheCreate
from app.services import artikel as artikel_svc
from app.services import ausleihe as ausleihe_svc
from app.services.export import export_artikel_csv, export_artikel_pdf


def get_db() -> Session:
    return SessionLocal()


# ──────────────────────────────────────────────
# Hauptgruppe
# ──────────────────────────────────────────────
@click.group()
def cli():
    """Veranstaltungstechnik Inventarsystem – CLI"""
    pass


# ──────────────────────────────────────────────
# Artikel
# ──────────────────────────────────────────────
@cli.group()
def artikel():
    """Artikel verwalten"""
    pass


@artikel.command("liste")
@click.option("--suche", "-s", default=None, help="Suchbegriff")
@click.option("--kategorie", "-k", default=None, type=int, help="Kategorie-ID")
@click.option("--verfuegbar", is_flag=True, help="Nur verfügbare Artikel")
def artikel_liste(suche, kategorie, verfuegbar):
    """Alle Artikel anzeigen"""
    db = get_db()
    items = artikel_svc.get_artikel_liste(
        db, suche=suche, kategorie_id=kategorie, nur_verfuegbar=verfuegbar
    )
    if not items:
        click.echo("Keine Artikel gefunden.")
        return
    click.echo(f"\n{'ID':<5} {'Name':<30} {'Verf.':<7} {'Gesamt':<8} {'Zustand':<14} {'Lagerort'}")
    click.echo("─" * 80)
    for a in items:
        click.echo(
            f"{a.id:<5} {a.name[:29]:<30} {a.menge_verfuegbar:<7} {a.menge_gesamt:<8} "
            f"{a.zustand.value:<14} {a.lagerort or '–'}"
        )
    click.echo(f"\n{len(items)} Artikel gefunden.\n")
    db.close()


@artikel.command("neu")
@click.option("--name", prompt="Name des Artikels")
@click.option("--menge", prompt="Gesamtmenge", type=int, default=1)
@click.option("--lagerort", prompt="Lagerort", default="")
@click.option("--kategorie", type=int, default=None)
def artikel_neu(name, menge, lagerort, kategorie):
    """Neuen Artikel anlegen"""
    db = get_db()
    data = ArtikelCreate(
        name=name,
        menge_gesamt=menge,
        lagerort=lagerort or None,
        kategorie_id=kategorie,
    )
    a = artikel_svc.create_artikel(db, data)
    click.echo(f"✓ Artikel '{a.name}' (ID {a.id}) angelegt.")
    db.close()


@artikel.command("export")
@click.option("--format", "fmt", type=click.Choice(["csv", "pdf"]), default="csv")
@click.option("--ausgabe", "-o", default=None, help="Ausgabedatei (Standard: inventar.csv/pdf)")
def artikel_export(fmt, ausgabe):
    """Inventarliste exportieren"""
    db = get_db()
    if fmt == "csv":
        data = export_artikel_csv(db)
        dateiname = ausgabe or "inventar.csv"
    else:
        data = export_artikel_pdf(db)
        dateiname = ausgabe or "inventar.pdf"
    with open(dateiname, "wb") as f:
        f.write(data)
    click.echo(f"✓ Export gespeichert: {dateiname}")
    db.close()


# ──────────────────────────────────────────────
# Ausleihe
# ──────────────────────────────────────────────
@cli.group()
def ausleihe():
    """Ausleihen verwalten"""
    pass


@ausleihe.command("liste")
@click.option("--aktiv", is_flag=True, help="Nur aktive Ausleihen")
def ausleihe_liste(aktiv):
    """Ausleihen anzeigen"""
    db = get_db()
    items = ausleihe_svc.get_ausleihen(db, nur_aktiv=aktiv)
    if not items:
        click.echo("Keine Ausleihen gefunden.")
        return
    click.echo(f"\n{'ID':<5} {'Artikel':<25} {'Entleiher':<20} {'Menge':<7} {'Status'}")
    click.echo("─" * 70)
    for a in items:
        status = "aktiv" if a.ist_aktiv else "zurückgegeben"
        artikel_name = a.artikel.name[:24] if a.artikel else str(a.artikel_id)
        click.echo(f"{a.id:<5} {artikel_name:<25} {a.entleiher_name[:19]:<20} {a.menge:<7} {status}")
    db.close()


@ausleihe.command("neu")
@click.option("--artikel-id", prompt="Artikel-ID", type=int)
@click.option("--entleiher", prompt="Name des Entleihers")
@click.option("--menge", prompt="Menge", type=int, default=1)
def ausleihe_neu(artikel_id, entleiher, menge):
    """Neue Ausleihe anlegen"""
    db = get_db()
    data = AusleiheCreate(artikel_id=artikel_id, entleiher_name=entleiher, menge=menge)
    try:
        a = ausleihe_svc.create_ausleihe(db, data)
        click.echo(f"✓ Ausleihe #{a.id} für '{entleiher}' angelegt.")
    except Exception as e:
        click.echo(f"✗ Fehler: {e}", err=True)
    db.close()


@ausleihe.command("rueckgabe")
@click.argument("ausleihe_id", type=int)
def ausleihe_rueckgabe(ausleihe_id):
    """Artikel zurückbuchen"""
    db = get_db()
    try:
        a = ausleihe_svc.rueckgabe(db, ausleihe_id)
        click.echo(f"✓ Ausleihe #{a.id} zurückgebucht.")
    except Exception as e:
        click.echo(f"✗ Fehler: {e}", err=True)
    db.close()


# ──────────────────────────────────────────────
# DB initialisieren
# ──────────────────────────────────────────────
@cli.command("init-db")
def init_db():
    """Datenbank-Tabellen erstellen"""
    create_tables()
    click.echo("✓ Datenbank initialisiert.")


if __name__ == "__main__":
    cli()