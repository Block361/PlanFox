from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from fastapi import HTTPException
from app.models import Artikel, ArtikelZustand, Ausleihe
from app.schemas import ArtikelCreate, ArtikelUpdate


def get_artikel(db: Session, artikel_id: int) -> Optional[Artikel]:
    return db.query(Artikel).filter(Artikel.id == artikel_id).first()


def get_artikel_liste(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    kategorie_id: Optional[int] = None,
    zustand: Optional[ArtikelZustand] = None,
    suche: Optional[str] = None,
    nur_verfuegbar: bool = False,
) -> list[Artikel]:
    q = db.query(Artikel)
    if kategorie_id:
        q = q.filter(Artikel.kategorie_id == kategorie_id)
    if zustand:
        q = q.filter(Artikel.zustand == zustand)
    if suche:
        q = q.filter(or_(
            Artikel.name.ilike(f"%{suche}%"),
            Artikel.seriennummer.ilike(f"%{suche}%"),
            Artikel.lagerort.ilike(f"%{suche}%"),
        ))
    if nur_verfuegbar:
        q = q.filter(Artikel.menge_verfuegbar > 0)
    return q.offset(skip).limit(limit).all()


def create_artikel(db: Session, data: ArtikelCreate) -> Artikel:
    from app.services.einheiten import create_einheiten_fuer_artikel
    artikel = Artikel(
        **data.model_dump(exclude={"menge_verfuegbar"}),
        menge_verfuegbar=data.menge_verfuegbar if data.menge_verfuegbar is not None else data.menge_gesamt,
    )
    db.add(artikel)
    db.commit()
    db.refresh(artikel)
    # Automatisch Einheiten mit Seriennummern erstellen
    create_einheiten_fuer_artikel(db, artikel, artikel.menge_gesamt)
    return artikel


def update_artikel(db: Session, artikel_id: int, data: ArtikelUpdate) -> Optional[Artikel]:
    from app.models import ArtikelEinheit
    from app.services.einheiten import create_einheiten_fuer_artikel
    artikel = get_artikel(db, artikel_id)
    if not artikel:
        return None
    alte_menge = artikel.menge_gesamt
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(artikel, field, value)
    db.commit()
    db.refresh(artikel)
    # Wenn Menge erhöht wurde: neue Einheiten generieren
    if data.menge_gesamt and data.menge_gesamt > alte_menge:
        zusatz = data.menge_gesamt - alte_menge
        create_einheiten_fuer_artikel(db, artikel, zusatz)
    return artikel


def delete_artikel(db: Session, artikel_id: int) -> bool:
    artikel = get_artikel(db, artikel_id)
    if not artikel:
        return False
    aktive = db.query(Ausleihe).filter(
        Ausleihe.artikel_id == artikel_id,
        Ausleihe.ist_aktiv == True
    ).count()
    if aktive > 0:
        raise HTTPException(
            status_code=409,
            detail=f"Artikel hat {aktive} aktive Ausleihe(n) – zuerst zurückbuchen"
        )
    db.query(Ausleihe).filter(Ausleihe.artikel_id == artikel_id).update(
        {"artikel_id": None}, synchronize_session=False
    )
    db.delete(artikel)
    db.commit()
    return True