import re
from sqlalchemy.orm import Session
from app.models import Artikel, ArtikelEinheit


def _generate_prefix(name: str) -> str:
    name_up = name.upper()
    laenge = re.search(r'(\d+[\.,]?\d*)\s*M\b', name_up)
    laenge_str = laenge.group(0).replace(' ', '').replace(',', '.') if laenge else ''
    kuerzel_map = {
        'XLR': 'XLR', 'DMX': 'DMX', 'HDMI': 'HDMI', 'SDI': 'SDI',
        'CAT': 'CAT', 'ETHERNET': 'ETH', 'STROMKABEL': 'STR',
        'SCHUKO': 'SCH', 'SPEAKON': 'SPK', 'KLINKE': 'KLK',
        'LAUTSPRECHER': 'LSP', 'SUBWOOFER': 'SUB', 'MIKROFON': 'MIC',
        'STATIV': 'STV', 'CASE': 'CASE', 'MISCHPULT': 'MXR',
        'VERSTAERKER': 'AMP', 'VERSTÄRKER': 'AMP',
    }
    prefix = 'ART'
    for key, val in kuerzel_map.items():
        if key in name_up:
            prefix = val
            break
    return f"{prefix}-{laenge_str}" if laenge_str else prefix


def generate_seriennummer(db: Session, artikel: Artikel) -> str:
    prefix = _generate_prefix(artikel.name)
    existing = (
        db.query(ArtikelEinheit.seriennummer)
        .filter(ArtikelEinheit.seriennummer.like(f"{prefix}-%"))
        .all()
    )
    max_nr = 0
    for (sn,) in existing:
        m = re.search(r'-(\d+)$', sn)
        if m:
            max_nr = max(max_nr, int(m.group(1)))
    return f"{prefix}-{max_nr + 1:03d}"


def create_einheiten_fuer_artikel(db: Session, artikel: Artikel, anzahl: int) -> list[ArtikelEinheit]:
    einheiten = []
    for _ in range(anzahl):
        sn = generate_seriennummer(db, artikel)
        einheit = ArtikelEinheit(artikel_id=artikel.id, seriennummer=sn)
        db.add(einheit)
        db.flush()
        einheiten.append(einheit)
    db.commit()
    for e in einheiten:
        db.refresh(e)
    return einheiten


def get_einheiten(db: Session, artikel_id: int) -> list[ArtikelEinheit]:
    return (
        db.query(ArtikelEinheit)
        .filter(ArtikelEinheit.artikel_id == artikel_id)
        .order_by(ArtikelEinheit.seriennummer)
        .all()
    )


def get_einheit_by_seriennummer(db: Session, sn: str):
    return db.query(ArtikelEinheit).filter(ArtikelEinheit.seriennummer == sn).first()