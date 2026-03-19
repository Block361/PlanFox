import io
from fastapi import APIRouter, Depends, UploadFile, File, Query
from fastapi.responses import Response
from sqlalchemy.orm import Session
from app.database import get_db
from app.services.vtinv import (
    export_vtinv, import_vtinv, parse_vtinv, VtinvParseError,
    VTINV_MIME, VTINV_EXT
)
from typing import Optional

router = APIRouter(prefix="/io", tags=["Import / Export"])


@router.get("/export.vtinv")
def export(
    ids: Optional[str] = Query(None, description="Komma-getrennte Artikel-IDs, leer = alle"),
    db: Session = Depends(get_db),
):
    """Exportiert Artikel als .vtinv Datei."""
    artikel_ids = [int(i) for i in ids.split(",") if i.strip()] if ids else None
    data = export_vtinv(db, artikel_ids)
    return Response(
        content=data,
        media_type=VTINV_MIME,
        headers={"Content-Disposition": f"attachment; filename=inventar.vtinv"},
    )


@router.post("/import")
async def importieren(
    file: UploadFile = File(...),
    ueberschreiben: bool = Query(False, description="Bestehende Artikel aktualisieren"),
    db: Session = Depends(get_db),
):
    """Importiert Artikel aus einer .vtinv Datei."""
    if not file.filename.endswith(".vtinv"):
        return {"fehler": "Nur .vtinv Dateien werden akzeptiert"}

    data = await file.read()
    try:
        stats = import_vtinv(db, data, ueberschreiben=ueberschreiben)
    except VtinvParseError as e:
        return {"fehler": str(e)}

    return {
        "status": "ok",
        "neu": stats["neu"],
        "aktualisiert": stats["aktualisiert"],
        "uebersprungen": stats["uebersprungen"],
        "fehler": stats["fehler"],
        "importierte_artikel": stats["artikel"],
    }


@router.post("/vorschau")
async def vorschau(file: UploadFile = File(...)):
    """Zeigt Inhalt einer .vtinv Datei ohne zu importieren."""
    data = await file.read()
    try:
        payload = parse_vtinv(data)
    except VtinvParseError as e:
        return {"fehler": str(e)}

    return {
        "version": payload.get("__vtinv__"),
        "erstellt_am": payload.get("erstellt_am"),
        "quelle": payload.get("quelle"),
        "anzahl": payload.get("anzahl"),
        "artikel": [
            {
                "name": a.get("name"),
                "menge": a.get("menge_gesamt"),
                "zustand": a.get("zustand"),
                "einheiten": len(a.get("einheiten", [])),
            }
            for a in payload.get("artikel", [])
        ],
    }