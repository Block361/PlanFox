from datetime import datetime
from typing import Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException, status
from app.models import Ausleihe, Artikel
from app.schemas import AusleiheCreate


def get_ausleihe(db: Session, ausleihe_id: int) -> Optional[Ausleihe]:
    return db.query(Ausleihe).filter(Ausleihe.id == ausleihe_id).first()


def get_ausleihen(
    db: Session,
    skip: int = 0,
    limit: int = 100,
    nur_aktiv: bool = False,
    artikel_id: Optional[int] = None,
    job_id: Optional[int] = None,
) -> list[Ausleihe]:
    q = db.query(Ausleihe)
    if nur_aktiv:
        q = q.filter(Ausleihe.ist_aktiv == True)
    if artikel_id:
        q = q.filter(Ausleihe.artikel_id == artikel_id)
    if job_id:
        q = q.filter(Ausleihe.job_id == job_id)
    return q.order_by(Ausleihe.ausgeliehen_am.desc()).offset(skip).limit(limit).all()


def create_ausleihe(db: Session, data: AusleiheCreate) -> Ausleihe:
    artikel = db.query(Artikel).filter(Artikel.id == data.artikel_id).first()
    if not artikel:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    if artikel.menge_verfuegbar < data.menge:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Nur {artikel.menge_verfuegbar} Stück verfügbar, {data.menge} angefragt",
        )
    ausleihe = Ausleihe(**data.model_dump())
    artikel.menge_verfuegbar -= data.menge
    db.add(ausleihe)
    db.commit()
    db.refresh(ausleihe)
    return ausleihe


def rueckgabe(db: Session, ausleihe_id: int) -> Ausleihe:
    ausleihe = get_ausleihe(db, ausleihe_id)
    if not ausleihe:
        raise HTTPException(status_code=404, detail="Ausleihe nicht gefunden")
    if not ausleihe.ist_aktiv:
        raise HTTPException(status_code=400, detail="Artikel bereits zurückgegeben")

    ausleihe.ist_aktiv = False
    ausleihe.zurueckgegeben_am = datetime.utcnow()

    artikel = db.query(Artikel).filter(Artikel.id == ausleihe.artikel_id).first()
    if artikel:
        artikel.menge_verfuegbar += ausleihe.menge

    db.commit()
    db.refresh(ausleihe)
    return ausleihe
