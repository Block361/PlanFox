import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import Artikel, ArtikelEinheit, ArtikelZustand
from app.services.einheiten import get_einheiten, create_einheiten_fuer_artikel, get_einheit_by_seriennummer

router = APIRouter(prefix="/einheiten", tags=["Einheiten"])


class EinheitenGenerieren(BaseModel):
    anzahl: int = 1


class EinheitUpdate(BaseModel):
    zustand: Optional[ArtikelZustand] = None
    notizen: Optional[str] = None


# ── Liste pro Artikel ─────────────────────────────────────────
@router.get("/artikel/{artikel_id}")
def liste(artikel_id: int, db: Session = Depends(get_db)):
    artikel = db.query(Artikel).filter(Artikel.id == artikel_id).first()
    if not artikel:
        raise HTTPException(404, "Artikel nicht gefunden")
    einheiten = get_einheiten(db, artikel_id)
    return [
        {
            "id": e.id,
            "seriennummer": e.seriennummer,
            "zustand": e.zustand,
            "notizen": e.notizen,
            "erstellt_am": e.erstellt_am,
        }
        for e in einheiten
    ]


# ── Generieren ────────────────────────────────────────────────
@router.post("/artikel/{artikel_id}/generieren")
def generieren(artikel_id: int, body: EinheitenGenerieren, db: Session = Depends(get_db)):
    artikel = db.query(Artikel).filter(Artikel.id == artikel_id).first()
    if not artikel:
        raise HTTPException(404, "Artikel nicht gefunden")
    einheiten = create_einheiten_fuer_artikel(db, artikel, body.anzahl)
    return [{"id": e.id, "seriennummer": e.seriennummer} for e in einheiten]


# ── Einzelne Einheit per SN ───────────────────────────────────
@router.get("/sn/{seriennummer}")
def get_by_sn(seriennummer: str, db: Session = Depends(get_db)):
    e = get_einheit_by_seriennummer(db, seriennummer)
    if not e:
        raise HTTPException(404, "Seriennummer nicht gefunden")
    return {
        "id": e.id,
        "seriennummer": e.seriennummer,
        "zustand": e.zustand,
        "notizen": e.notizen,
        "erstellt_am": e.erstellt_am,
        "artikel_id": e.artikel_id,
    }


# ── Einheit bearbeiten ────────────────────────────────────────
@router.patch("/{seriennummer}")
def update(seriennummer: str, data: EinheitUpdate, db: Session = Depends(get_db)):
    e = get_einheit_by_seriennummer(db, seriennummer)
    if not e:
        raise HTTPException(404, "Seriennummer nicht gefunden")
    if data.zustand is not None:
        e.zustand = data.zustand
    if data.notizen is not None:
        e.notizen = data.notizen
    db.commit()
    db.refresh(e)
    return {"id": e.id, "seriennummer": e.seriennummer, "zustand": e.zustand, "notizen": e.notizen}


# ── QR-Code SVG ───────────────────────────────────────────────
@router.get("/qr/{seriennummer}.svg")
def qr_svg(seriennummer: str, db: Session = Depends(get_db)):
    import qrcode
    import qrcode.image.svg
    e = get_einheit_by_seriennummer(db, seriennummer)
    if not e:
        raise HTTPException(404, "Seriennummer nicht gefunden")
    daten = f"SN:{seriennummer}|TYP:{e.artikel.name}"
    factory = qrcode.image.svg.SvgPathImage
    img = qrcode.make(daten, image_factory=factory, box_size=8, border=2)
    buf = io.BytesIO()
    img.save(buf)
    return Response(content=buf.getvalue(), media_type="image/svg+xml")


# ── Druckseite ────────────────────────────────────────────────
@router.get("/drucken/{artikel_id}", response_class=HTMLResponse)
def druckseite(artikel_id: int, db: Session = Depends(get_db)):
    import qrcode
    import qrcode.image.svg
    artikel = db.query(Artikel).filter(Artikel.id == artikel_id).first()
    if not artikel:
        raise HTTPException(404, "Artikel nicht gefunden")
    einheiten = get_einheiten(db, artikel_id)
    if not einheiten:
        return HTMLResponse("<p style='font-family:monospace;padding:20px'>Keine Einheiten vorhanden.</p>")

    karten = []
    for e in einheiten:
        daten = f"SN:{e.seriennummer}|TYP:{artikel.name}"
        factory = qrcode.image.svg.SvgPathImage
        img = qrcode.make(daten, image_factory=factory, box_size=6, border=2)
        buf = io.BytesIO()
        img.save(buf)
        svg_str = buf.getvalue().decode("utf-8")
        karten.append(f"""
        <div class="karte">
          <div class="qr">{svg_str}</div>
          <div class="info">
            <div class="typ">{artikel.name}</div>
            <div class="sn">{e.seriennummer}</div>
            {f'<div class="ort">{artikel.lagerort}</div>' if artikel.lagerort else ''}
          </div>
        </div>""")

    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8"><title>QR – {artikel.name}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{font-family:'Courier New',monospace;background:#fff;color:#000;}}
h1{{font-size:13px;padding:10px 14px;border-bottom:1px solid #ccc;}}
.grid{{display:flex;flex-wrap:wrap;gap:6px;padding:12px;}}
.karte{{border:1px solid #000;padding:6px;width:150px;display:flex;flex-direction:column;align-items:center;page-break-inside:avoid;}}
.qr svg{{width:110px;height:110px;}}
.info{{text-align:center;margin-top:4px;}}
.typ{{font-size:8px;color:#555;line-height:1.3;}}
.sn{{font-size:11px;font-weight:bold;margin-top:2px;letter-spacing:.04em;}}
.ort{{font-size:8px;color:#888;margin-top:1px;}}
.btn-print{{position:fixed;top:10px;right:14px;background:#000;color:#fff;border:none;padding:7px 14px;cursor:pointer;font-family:inherit;font-size:12px;}}
@media print{{.btn-print{{display:none;}}}}
</style></head>
<body>
<button class="btn-print" onclick="window.print()">🖨 Drucken</button>
<h1>QR-Codes · {artikel.name} · {len(einheiten)} Stück</h1>
<div class="grid">{''.join(karten)}</div>
</body></html>""")