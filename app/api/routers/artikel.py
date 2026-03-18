from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.schemas import ArtikelCreate, ArtikelUpdate, ArtikelOut
from app.services import artikel as svc
from app.services.export import export_artikel_csv, export_artikel_pdf
from app.models import ArtikelZustand
import io

router = APIRouter(prefix="/artikel", tags=["Artikel"])


@router.get("/", response_model=list[ArtikelOut])
def liste(
    skip: int = 0,
    limit: int = 100,
    kategorie_id: Optional[int] = None,
    zustand: Optional[ArtikelZustand] = None,
    suche: Optional[str] = None,
    nur_verfuegbar: bool = False,
    db: Session = Depends(get_db),
):
    return svc.get_artikel_liste(db, skip, limit, kategorie_id, zustand, suche, nur_verfuegbar)


@router.get("/{artikel_id}", response_model=ArtikelOut)
def detail(artikel_id: int, db: Session = Depends(get_db)):
    a = svc.get_artikel(db, artikel_id)
    if not a:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    return a


@router.post("/", response_model=ArtikelOut, status_code=201)
def erstellen(data: ArtikelCreate, db: Session = Depends(get_db)):
    return svc.create_artikel(db, data)


@router.patch("/{artikel_id}", response_model=ArtikelOut)
def aktualisieren(artikel_id: int, data: ArtikelUpdate, db: Session = Depends(get_db)):
    a = svc.update_artikel(db, artikel_id, data)
    if not a:
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")
    return a


@router.delete("/{artikel_id}", status_code=204)
def loeschen(artikel_id: int, db: Session = Depends(get_db)):
    if not svc.delete_artikel(db, artikel_id):
        raise HTTPException(status_code=404, detail="Artikel nicht gefunden")


@router.get("/export/csv")
def export_csv(db: Session = Depends(get_db)):
    data = export_artikel_csv(db)
    return StreamingResponse(
        io.BytesIO(data),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=inventar.csv"},
    )


@router.get("/export/pdf")
def export_pdf(db: Session = Depends(get_db)):
    data = export_artikel_pdf(db)
    return StreamingResponse(
        io.BytesIO(data),
        media_type="application/pdf",
        headers={"Content-Disposition": "attachment; filename=inventar.pdf"},
    )
