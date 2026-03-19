from typing import Optional
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import Job, JobStatus
from app.schemas import JobCreate, JobUpdate, JobOut

router = APIRouter(prefix="/jobs", tags=["Jobs"])


@router.get("/", response_model=list[JobOut])
def liste(
    skip: int = 0,
    limit: int = 100,
    status: Optional[JobStatus] = None,
    db: Session = Depends(get_db),
):
    q = db.query(Job)
    if status:
        q = q.filter(Job.status == status)
    return q.order_by(Job.beginn.desc()).offset(skip).limit(limit).all()


@router.get("/{job_id}", response_model=JobOut)
def detail(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job nicht gefunden")
    return job


@router.post("/", response_model=JobOut, status_code=201)
def erstellen(data: JobCreate, db: Session = Depends(get_db)):
    job = Job(**data.model_dump())
    db.add(job)
    db.commit()
    db.refresh(job)
    return job


@router.patch("/{job_id}", response_model=JobOut)
def aktualisieren(job_id: int, data: JobUpdate, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job nicht gefunden")
    for field, value in data.model_dump(exclude_unset=True).items():
        setattr(job, field, value)
    db.commit()
    db.refresh(job)
    return job


@router.delete("/{job_id}", status_code=204)
def loeschen(job_id: int, db: Session = Depends(get_db)):
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job nicht gefunden")
    db.delete(job)
    db.commit()


from fastapi.responses import HTMLResponse

@router.get("/{job_id}/qr", response_class=HTMLResponse)
def job_qr_seite(job_id: int, db: Session = Depends(get_db)):
    import io, qrcode, qrcode.image.svg
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(status_code=404, detail="Job nicht gefunden")
    daten = f"JOB:{job_id}"
    img = qrcode.make(daten, image_factory=qrcode.image.svg.SvgPathImage, box_size=10, border=3)
    buf = io.BytesIO()
    img.save(buf)
    svg = buf.getvalue().decode("utf-8")
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="de"><head><meta charset="UTF-8"><title>QR – {job.name}</title>
<style>
body{{font-family:'Courier New',monospace;background:#fff;color:#000;display:flex;flex-direction:column;align-items:center;padding:40px 20px;}}
h1{{font-size:18px;margin-bottom:4px;}}
p{{font-size:12px;color:#555;margin-bottom:24px;}}
.qr{{border:2px solid #000;padding:16px;}}
.qr svg{{width:220px;height:220px;display:block;}}
.info{{margin-top:16px;text-align:center;font-size:12px;color:#333;}}
button{{margin-top:20px;background:#000;color:#fff;border:none;padding:10px 24px;cursor:pointer;font-family:inherit;font-size:13px;}}
@media print{{button{{display:none;}}}}
</style></head>
<body>
<h1>{job.name}</h1>
<p>{job.veranstaltungsort or ''}{' · ' + job.kunde if job.kunde else ''}</p>
<div class="qr">{svg}</div>
<div class="info">Job-ID: {job_id} · Mit VT-Scan scannen</div>
<button onclick="window.print()">🖨 Drucken</button>
</body></html>""")


@router.get("/{job_id}/packliste", response_class=HTMLResponse)
def packliste(job_id: int, db: Session = Depends(get_db)):
    import io, qrcode, qrcode.image.svg
    from app.models import Ausleihe, Artikel, ArtikelEinheit

    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job nicht gefunden")

    ausleihen = db.query(Ausleihe).filter(
        Ausleihe.job_id == job_id,
        Ausleihe.ist_aktiv == True
    ).all()

    def make_qr(daten: str, size: int = 80) -> str:
        import re
        box = max(2, size // 25)
        img = qrcode.make(daten, image_factory=qrcode.image.svg.SvgPathImage, box_size=box, border=1)
        buf = io.BytesIO()
        img.save(buf)
        svg = buf.getvalue().decode("utf-8")
        # Entferne bestehende width/height, setze neue feste Größe
        svg = re.sub(r'\s+width="[^"]*"', '', svg)
        svg = re.sub(r'\s+height="[^"]*"', '', svg)
        svg = svg.replace('<svg ', f'<svg width="{size}" height="{size}" style="display:block;flex-shrink:0" ', 1)
        return svg

    # Job-QR
    job_qr = make_qr(f"JOB:{job_id}", size=120)

    # Artikel nach Lagerort gruppieren
    from collections import defaultdict
    gruppen = defaultdict(list)

    for aus in ausleihen:
        artikel = db.query(Artikel).filter(Artikel.id == aus.artikel_id).first()
        if not artikel:
            continue
        lagerort = artikel.lagerort or "Kein Lagerort"

        # Einheiten für diesen Artikel
        einheiten = db.query(ArtikelEinheit).filter(
            ArtikelEinheit.artikel_id == artikel.id
        ).limit(aus.menge).all()

        einheit_qrs = []
        for e in einheiten:
            qr_svg = make_qr(f"SN:{e.seriennummer}", size=60)
            einheit_qrs.append({"sn": e.seriennummer, "zustand": e.zustand.value, "qr": qr_svg})

        gruppen[lagerort].append({
            "artikel": artikel,
            "ausleihe": aus,
            "einheiten": einheit_qrs,
        })

    # HTML für Gruppen
    gruppen_html = ""
    for lagerort in sorted(gruppen.keys()):
        rows = ""
        for item in gruppen[lagerort]:
            a = item["artikel"]
            aus = item["ausleihe"]
            einheiten = item["einheiten"]

            # Technische Info
            tech = []
            if a.laenge_m: tech.append(f"{a.laenge_m} m")
            if a.stecker_a and a.stecker_b: tech.append(f"{a.stecker_a} → {a.stecker_b}")
            elif a.stecker_a: tech.append(a.stecker_a)
            if a.kabeltyp: tech.append(a.kabeltyp)
            tech_str = " · ".join(tech)

            # Einheiten-Pills mit QR
            einheit_html = ""
            for e in einheiten:
                farbe = "#006644" if e["zustand"] == "gut" else "#cc3300"
                einheit_html += f"""
                <div class="sn-item">
                    <div class="sn-qr">{e["qr"]}</div>
                    <div class="sn-info">
                        <div class="sn-code">{e["sn"]}</div>
                        <div class="sn-status" style="color:{farbe}">{e["zustand"]}</div>
                    </div>
                </div>"""

            rows += f"""
            <tr>
                <td class="check"><input type="checkbox"></td>
                <td class="artikel-name">
                    <strong>{a.name}</strong>
                    {f'<div class="tech">{tech_str}</div>' if tech_str else ''}
                    {f'<div class="tech">{a.hersteller}</div>' if a.hersteller else ''}
                </td>
                <td class="menge">{aus.menge}×</td>
                <td class="einheiten">{einheit_html if einheit_html else '<span class="no-sn">–</span>'}</td>
                <td class="notiz"></td>
            </tr>"""

        gruppen_html += f"""
        <div class="gruppe">
            <div class="gruppe-header">📦 {lagerort}</div>
            <table>
                <thead>
                    <tr>
                        <th class="check">✓</th>
                        <th>Artikel</th>
                        <th>Menge</th>
                        <th>Seriennummern</th>
                        <th>Notiz</th>
                    </tr>
                </thead>
                <tbody>{rows}</tbody>
            </table>
        </div>"""

    if not gruppen_html:
        gruppen_html = '<p style="color:#888;padding:20px">Keine aktiven Ausleihen für diesen Job.</p>'

    beginn_str = job.beginn.strftime("%d.%m.%Y %H:%M") if job.beginn else "–"
    ende_str = job.ende.strftime("%d.%m.%Y %H:%M") if job.ende else "–"
    gesamt = sum(a.menge for a in ausleihen)

    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<title>Packliste – {job.name}</title>
<style>
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
body {{ font-family: 'Courier New', monospace; font-size: 11px; color: #000; background: #fff; }}

/* ── Header ── */
.header {{ display: flex; justify-content: space-between; align-items: flex-start; padding: 20px 24px 16px; border-bottom: 2px solid #000; }}
.header-left h1 {{ font-size: 20px; font-weight: bold; margin-bottom: 4px; }}
.header-left .meta {{ font-size: 10px; color: #444; line-height: 1.8; }}
.header-left .status {{ display: inline-block; border: 1px solid #000; padding: 2px 8px; font-size: 9px; letter-spacing: .1em; text-transform: uppercase; margin-top: 6px; }}
.job-qr {{ text-align: center; }}
.job-qr svg {{ display: block; }}
.job-qr .qr-label {{ font-size: 9px; color: #666; margin-top: 4px; text-align: center; }}

/* ── Zusammenfassung ── */
.summary {{ display: flex; gap: 0; border-bottom: 1px solid #ccc; }}
.summary-item {{ flex: 1; padding: 8px 16px; border-right: 1px solid #ccc; }}
.summary-item:last-child {{ border-right: none; }}
.summary-item .label {{ font-size: 8px; letter-spacing: .15em; text-transform: uppercase; color: #888; }}
.summary-item .value {{ font-size: 14px; font-weight: bold; margin-top: 2px; }}

/* ── Gruppen ── */
.gruppe {{ margin: 0; page-break-inside: avoid; }}
.gruppe-header {{ background: #000; color: #fff; padding: 6px 16px; font-size: 11px; font-weight: bold; letter-spacing: .08em; }}

table {{ width: 100%; border-collapse: collapse; }}
th {{ padding: 5px 10px; font-size: 9px; letter-spacing: .12em; text-transform: uppercase; border-bottom: 1px solid #000; text-align: left; background: #f5f5f5; }}
td {{ padding: 8px 10px; border-bottom: 1px solid #ddd; vertical-align: top; }}

th.check, td.check {{ width: 22px; text-align: center; }}
td.check input {{ width: 14px; height: 14px; cursor: pointer; }}
td.menge {{ width: 40px; font-weight: bold; text-align: center; font-size: 13px; }}
td.notiz {{ width: 80px; border-bottom: 1px solid #ddd; }}
td.notiz::after {{ content: ''; display: block; border-bottom: 1px dotted #ccc; margin-top: 16px; }}

.artikel-name strong {{ font-size: 12px; }}
.tech {{ font-size: 9px; color: #666; margin-top: 2px; }}

/* ── Einheiten ── */
.einheiten {{ width: 280px; }}
.sn-item {{ display: inline-flex; align-items: center; gap: 4px; margin: 2px 4px 2px 0; border: 1px solid #ddd; padding: 2px 4px; }}
.sn-qr svg {{ display: block; }}
.sn-info {{ font-size: 9px; line-height: 1.4; }}
.sn-code {{ font-weight: bold; letter-spacing: .04em; }}
.sn-status {{ font-size: 8px; }}
.no-sn {{ color: #aaa; font-size: 10px; }}

/* ── Footer ── */
.footer {{ border-top: 1px solid #ccc; padding: 10px 24px; display: flex; justify-content: space-between; font-size: 9px; color: #888; margin-top: 8px; }}

/* ── Print ── */
.print-btn {{ position: fixed; top: 12px; right: 16px; background: #000; color: #fff; border: none; padding: 8px 18px; cursor: pointer; font-family: inherit; font-size: 12px; z-index: 100; }}
@media print {{
    .print-btn {{ display: none; }}
    .gruppe {{ page-break-inside: avoid; }}
}}
</style>
</head>
<body>
<button class="print-btn" onclick="window.print()">🖨 Drucken</button>

<div class="header">
    <div class="header-left">
        <h1>{job.name}</h1>
        <div class="meta">
            {'Kunde: ' + job.kunde + '<br>' if job.kunde else ''}
            {'Ort: ' + job.veranstaltungsort + '<br>' if job.veranstaltungsort else ''}
            Beginn: {beginn_str}<br>
            Ende: {ende_str}
        </div>
        <div class="status">{job.status.value}</div>
    </div>
    <div class="job-qr">
        {job_qr}
        <div class="qr-label">Job #{job_id}</div>
    </div>
</div>

<div class="summary">
    <div class="summary-item">
        <div class="label">Positionen</div>
        <div class="value">{len(ausleihen)}</div>
    </div>
    <div class="summary-item">
        <div class="label">Stück gesamt</div>
        <div class="value">{gesamt}</div>
    </div>
    <div class="summary-item">
        <div class="label">Lagerorte</div>
        <div class="value">{len(gruppen)}</div>
    </div>
    <div class="summary-item">
        <div class="label">Erstellt</div>
        <div class="value" style="font-size:11px">{"__DATUM__"}</div>
    </div>
</div>

{gruppen_html}

<div class="footer">
    <span>VT-Inventar · Packliste Job #{job_id} · {job.name}</span>
    <span>Seite <span class="page-num"></span></span>
</div>

<script>
document.querySelector('.value[style*="font-size:11px"]').textContent =
    new Date().toLocaleString('de-DE', {{day:'2-digit',month:'2-digit',year:'numeric',hour:'2-digit',minute:'2-digit'}});
</script>
</body>
</html>""")