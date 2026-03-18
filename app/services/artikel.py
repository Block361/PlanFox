from typing import Optional
from sqlalchemy.orm import Session
from sqlalchemy import or_
from app.models import Artikel, ArtikelZustand
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
        q = q.filter(
            or_(
                Artikel.name.ilike(f"%{suche}%"),
                Artikel.seriennummer.ilike(f"%{suche}%"),
                Artikel.lagerort.ilike(f"%{suche}%"),
            )
        )
    if nur_verfuegbar:
        q = q.filter(Artikel.menge_verfuegbar > 0)
    return q.offset(skip).limit(limit).all()


def create_artikel(db: Session, data: ArtikelCreate) -> Artikel:
    artikel = Artikel(
        **data.model_dump(exclude={"menge_verfuegbar"}),
        menge_verfuegbar=data.menge_verfuegbar if data.menge_verfuegbar is not None else data.menge_gesamt,
    )
    db.add(artikel)
    db.commit()
    db.refresh(artikel)
    return artikel


def update_artikel(db: Session, artikel_id: int, data: ArtikelUpdate) -> Optional[Artikel]:
    artikel = get_artikel(db, artikel_id)
    if not artikel:
        return None
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(artikel, field, value)
    db.commit()
    db.refresh(artikel)
    return artikel


def delete_artikel(db: Session, artikel_id: int) -> bool:
    artikel = get_artikel(db, artikel_id)
    if not artikel:
        return False
    db.delete(artikel)
    db.commit()
    return True
