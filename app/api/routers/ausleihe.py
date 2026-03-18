from typing import Optional
from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import AusleiheCreate, AusleiheOut
from app.services import ausleihe as svc
from app.services.export import export_ausleihen_csv
import io

router = APIRouter(prefix="/ausleihen", tags=["Ausleihe"])


@router.get("/", response_model=list[AusleiheOut])
def liste(
    skip: int = 0,
    limit: int = 100,
    nur_aktiv: bool = False,
    artikel_id: Optional[int] = None,
    job_id: Optional[int] = None,
    db: Session = Depends(get_db),
):
    return svc.get_ausleihen(db, skip, limit, nur_aktiv, artikel_id, job_id)


@router.post("/", response_model=AusleiheOut, status_code=201)
def erstellen(data: AusleiheCreate, db: Session = Depends(get_db)):
    return svc.create_ausleihe(db, data)


@router.post("/{ausleihe_id}/rueckgabe", response_model=AusleiheOut)
def rueckgabe(ausleihe_id: int, db: Session = Depends(get_db)):
    return svc.rueckgabe(db, ausleihe_id)


@router.get("/export/csv")
def export_csv(nur_aktiv: bool = False, db: Session = Depends(get_db)):
    data = export_ausleihen_csv(db, nur_aktiv)
    return StreamingResponse(
        io.BytesIO(data),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=ausleihen.csv"},
    )


from pydantic import BaseModel
from typing import Optional
from datetime import datetime as dt

class AusleiheUpdate(BaseModel):
    entleiher_name: Optional[str] = None
    entleiher_kontakt: Optional[str] = None
    menge: Optional[int] = None
    rueckgabe_geplant: Optional[dt] = None
    notizen: Optional[str] = None

@router.patch("/{ausleihe_id}", response_model=AusleiheOut)
def aktualisieren(ausleihe_id: int, data: AusleiheUpdate, db: Session = Depends(get_db)):
    from app.models import Ausleihe as AusleiheModel
    a = db.query(AusleiheModel).filter(AusleiheModel.id == ausleihe_id).first()
    if not a:
        from fastapi import HTTPException
        raise HTTPException(404, "Ausleihe nicht gefunden")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(a, field, value)
    db.commit()
    db.refresh(a)
    return a