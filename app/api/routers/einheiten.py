from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Artikel
from app.services.einheiten import get_einheiten, create_einheiten_fuer_artikel, get_einheit_by_seriennummer

router = APIRouter(prefix="/einheiten", tags=["Einheiten"])


@router.get("/artikel/{artikel_id}")
def liste(artikel_id: int, db: Session = Depends(get_db)):
    artikel = db.query(Artikel).filter(Artikel.id == artikel_id).first()
    if not artikel:
        raise HTTPException(404, "Artikel nicht gefunden")
    einheiten = get_einheiten(db, artikel_id)
    return {
        "artikel": {"id": artikel.id, "name": artikel.name},
        "einheiten": [{"id": e.id, "seriennummer": e.seriennummer, "zustand": e.zustand} for e in einheiten]
    }


@router.post("/artikel/{artikel_id}/generieren")
def generieren(artikel_id: int, anzahl: int = 1, db: Session = Depends(get_db)):
    artikel = db.query(Artikel).filter(Artikel.id == artikel_id).first()
    if not artikel:
        raise HTTPException(404, "Artikel nicht gefunden")
    einheiten = create_einheiten_fuer_artikel(db, artikel, anzahl)
    return [{"id": e.id, "seriennummer": e.seriennummer} for e in einheiten]


@router.get("/qr/{artikel_id}", response_class=HTMLResponse)
def qr_labels(artikel_id: int, db: Session = Depends(get_db)):
    artikel = db.query(Artikel).filter(Artikel.id == artikel_id).first()
    if not artikel:
        raise HTTPException(404, "Artikel nicht gefunden")
    einheiten = get_einheiten(db, artikel_id)
    if not einheiten:
        return HTMLResponse("<h2>Keine Einheiten vorhanden. Zuerst Seriennummern generieren.</h2>")

    labels_html = "\n".join([
        f'''<div class="label">
          <div class="qr" id="qr-{e.id}"></div>
          <div class="info">
            <div class="typ">{artikel.name}</div>
            <div class="sn">{e.seriennummer}</div>
          </div>
        </div>
        <script>new QRCode(document.getElementById("qr-{e.id}"), {{
          text: "{e.seriennummer}",
          width: 80, height: 80,
          colorDark: "#000", colorLight: "#fff",
          correctLevel: QRCode.CorrectLevel.M
        }});</script>'''
        for e in einheiten
    ])

    return HTMLResponse(f"""<!DOCTYPE html>
<html><head>
<meta charset="UTF-8">
<title>QR Labels – {artikel.name}</title>
<script src="https://cdnjs.cloudflare.com/ajax/libs/qrcodejs/1.0.0/qrcode.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Courier New', monospace; background: #f5f5f5; padding: 20px; }}
  h1 {{ font-size: 14px; margin-bottom: 16px; color: #333; }}
  .grid {{ display: flex; flex-wrap: wrap; gap: 8px; }}
  .label {{
    background: white; border: 1px solid #ccc;
    padding: 8px; display: flex; align-items: center; gap: 10px;
    width: 200px; page-break-inside: avoid;
  }}
  .qr canvas, .qr img {{ display: block; }}
  .info {{ flex: 1; }}
  .typ {{ font-size: 9px; color: #666; text-transform: uppercase; letter-spacing: 0.05em; line-height: 1.3; }}
  .sn {{ font-size: 13px; font-weight: bold; color: #000; margin-top: 2px; letter-spacing: 0.05em; }}
  .print-btn {{
    position: fixed; top: 16px; right: 16px;
    background: #000; color: #fff; border: none;
    padding: 10px 20px; font-family: inherit; font-size: 12px;
    cursor: pointer; letter-spacing: 0.1em;
  }}
  @media print {{
    .print-btn {{ display: none; }}
    body {{ background: white; padding: 8px; }}
  }}
</style>
</head><body>
<button class="print-btn" onclick="window.print()">⎙ DRUCKEN</button>
<h1>QR-Labels: {artikel.name} ({len(einheiten)} Stück)</h1>
<div class="grid">
{labels_html}
</div>
</body></html>""")


@router.get("/scan/{seriennummer}")
def scan(seriennummer: str, db: Session = Depends(get_db)):
    einheit = get_einheit_by_seriennummer(db, seriennummer)
    if not einheit:
        raise HTTPException(404, "Seriennummer nicht gefunden")
    artikel = einheit.artikel
    return {
        "seriennummer": einheit.seriennummer,
        "zustand": einheit.zustand,
        "artikel": {"id": artikel.id, "name": artikel.name, "lagerort": artikel.lagerort},
    }