"""
Mobile Scan-Router – QR-Code scannen und Artikel auf Job buchen.
Endpunkte:
  GET  /scan/          – Mobile Scan-Seite (HTML)
  GET  /scan/job/{id}.svg  – QR-Code für Job
  POST /scan/buchen    – Ausleihe anlegen
"""
import io
from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import HTMLResponse, Response
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional
from app.database import get_db
from app.models import Job, Artikel, ArtikelEinheit, Ausleihe

router = APIRouter(prefix="/scan", tags=["Scan"])


class BuchungRequest(BaseModel):
    job_id: int
    artikel_id: int
    entleiher_name: str
    menge: int = 1


# ── Job QR-Code ───────────────────────────────────────────────
@router.get("/job/{job_id}.svg")
def job_qr(job_id: int, db: Session = Depends(get_db)):
    import qrcode, qrcode.image.svg
    job = db.query(Job).filter(Job.id == job_id).first()
    if not job:
        raise HTTPException(404, "Job nicht gefunden")
    # Format: JOB:42
    daten = f"JOB:{job_id}"
    img = qrcode.make(daten, image_factory=qrcode.image.svg.SvgPathImage, box_size=8, border=2)
    buf = io.BytesIO()
    img.save(buf)
    return Response(content=buf.getvalue(), media_type="image/svg+xml")


# ── Ausleihe buchen ───────────────────────────────────────────
@router.post("/buchen")
def buchen(data: BuchungRequest, db: Session = Depends(get_db)):
    artikel = db.query(Artikel).filter(Artikel.id == data.artikel_id).first()
    if not artikel:
        raise HTTPException(404, "Artikel nicht gefunden")
    if artikel.menge_verfuegbar < data.menge:
        raise HTTPException(409, f"Nur {artikel.menge_verfuegbar} verfügbar")
    job = db.query(Job).filter(Job.id == data.job_id).first()
    if not job:
        raise HTTPException(404, "Job nicht gefunden")

    ausleihe = Ausleihe(
        artikel_id=data.artikel_id,
        job_id=data.job_id,
        entleiher_name=data.entleiher_name,
        menge=data.menge,
    )
    artikel.menge_verfuegbar -= data.menge
    db.add(ausleihe)
    db.commit()
    db.refresh(ausleihe)
    return {"id": ausleihe.id, "artikel": artikel.name, "job": job.name}


# ── Mobile Scan-Seite ─────────────────────────────────────────
@router.get("/", response_class=HTMLResponse)
def scan_seite(db: Session = Depends(get_db)):
    jobs = db.query(Job).filter(Job.status.in_(["geplant", "aktiv"])).order_by(Job.beginn).all()
    job_options = "".join(
        f'<option value="{j.id}">{j.name}{" – " + j.veranstaltungsort if j.veranstaltungsort else ""}</option>'
        for j in jobs
    )
    return HTMLResponse(f"""<!DOCTYPE html>
<html lang="de">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0">
<title>VT-Scan</title>
<style>
:root{{--bg:#0f0f0f;--s:#171717;--s2:#1f1f1f;--b:#2a2a2a;--acc:#d4f040;--acc2:#40f0a0;--danger:#f04060;--text:#e8e8e0;--muted:#666;--font:'DM Mono',monospace;}}
*{{box-sizing:border-box;margin:0;padding:0;}}
body{{background:var(--bg);color:var(--text);font-family:var(--font);min-height:100vh;padding:16px;}}
h1{{font-size:18px;font-weight:700;letter-spacing:-.01em;margin-bottom:4px;color:var(--acc);}}
.sub{{font-size:11px;color:var(--muted);margin-bottom:20px;}}
.card{{background:var(--s);border:1px solid var(--b);padding:16px;margin-bottom:14px;border-radius:2px;}}
.card-title{{font-size:9px;letter-spacing:.15em;text-transform:uppercase;color:var(--muted);margin-bottom:12px;}}
.badge{{display:inline-block;padding:3px 10px;font-size:10px;letter-spacing:.08em;text-transform:uppercase;border:1px solid;border-radius:2px;}}
.badge-job{{color:var(--acc);border-color:rgba(212,240,64,.4);background:rgba(212,240,64,.08);}}
.badge-artikel{{color:var(--acc2);border-color:rgba(64,240,160,.4);background:rgba(64,240,160,.08);}}
.badge-err{{color:var(--danger);border-color:rgba(240,64,96,.4);background:rgba(240,64,96,.08);}}
label{{font-size:10px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted);display:block;margin-bottom:5px;}}
select,input{{width:100%;background:var(--s2);border:1px solid var(--b);color:var(--text);font-family:var(--font);font-size:13px;padding:10px 12px;outline:none;margin-bottom:12px;}}
select:focus,input:focus{{border-color:var(--acc);}}
select option{{background:var(--s2);}}
.btn{{width:100%;padding:14px;font-family:var(--font);font-size:13px;letter-spacing:.06em;text-transform:uppercase;cursor:pointer;border:1px solid;font-weight:500;}}
.btn-primary{{background:var(--acc);color:#0f0f0f;border-color:var(--acc);}}
.btn-primary:hover{{background:#c8e030;}}
.btn-primary:disabled{{background:var(--b);color:var(--muted);border-color:var(--b);cursor:not-allowed;}}
.btn-ghost{{background:transparent;color:var(--muted);border-color:var(--b);margin-bottom:10px;}}
.btn-ghost:hover{{color:var(--text);border-color:var(--text);}}
.btn-danger{{background:transparent;color:var(--danger);border-color:rgba(240,64,96,.3);}}
.scan-area{{background:var(--s2);border:2px dashed var(--b);padding:20px;text-align:center;font-size:12px;color:var(--muted);margin-bottom:12px;cursor:pointer;transition:border-color .15s;}}
.scan-area:hover,.scan-area.active{{border-color:var(--acc);color:var(--text);}}
.scan-area .icon{{font-size:32px;margin-bottom:8px;display:block;}}
video{{width:100%;max-height:240px;object-fit:cover;border:1px solid var(--b);display:none;}}
video.active{{display:block;margin-bottom:12px;}}
.item-row{{display:flex;align-items:center;justify-content:space-between;padding:10px 0;border-bottom:1px solid var(--b);}}
.item-row:last-child{{border-bottom:none;}}
.item-name{{font-size:13px;}}
.item-sn{{font-size:10px;color:var(--muted);margin-top:2px;}}
.item-menge{{display:flex;align-items:center;gap:8px;}}
.item-menge button{{background:var(--s2);border:1px solid var(--b);color:var(--text);width:28px;height:28px;font-size:16px;cursor:pointer;display:flex;align-items:center;justify-content:center;}}
.item-menge span{{min-width:20px;text-align:center;font-size:13px;}}
.remove-btn{{color:var(--danger);background:transparent;border:none;font-size:16px;cursor:pointer;padding:4px;}}
#toast{{position:fixed;bottom:20px;left:16px;right:16px;background:var(--s);border:1px solid var(--b);border-left:3px solid var(--acc);padding:12px 16px;font-size:12px;transform:translateY(80px);opacity:0;transition:all .25s;z-index:100;}}
#toast.show{{transform:none;opacity:1;}}
#toast.error{{border-left-color:var(--danger);}}
.step{{display:none;}}.step.active{{display:block;}}
.progress{{display:flex;gap:6px;margin-bottom:20px;}}
.progress-dot{{flex:1;height:3px;background:var(--b);transition:background .2s;}}
.progress-dot.done{{background:var(--acc);}}
.progress-dot.active{{background:var(--acc2);}}
</style>
</head>
<body>
<h1>VT–Scan</h1>
<div class="sub">Equipment auf Job buchen</div>

<div class="progress">
  <div class="progress-dot active" id="dot-1"></div>
  <div class="progress-dot" id="dot-2"></div>
  <div class="progress-dot" id="dot-3"></div>
</div>

<!-- Schritt 1: Job wählen -->
<div class="step active" id="step-1">
  <div class="card">
    <div class="card-title">1 · Job auswählen</div>
    <label>Job</label>
    <select id="job-select">
      <option value="">– Job wählen –</option>
      {job_options}
    </select>
    <div class="scan-area" id="job-scan-area" onclick="startScan('job')">
      <span class="icon">⬡</span>
      Job-QR scannen
    </div>
    <video id="job-video" playsinline></video>
    <div style="display:flex;gap:8px;margin-bottom:12px;">
      <input id="job-id-manual" placeholder="Job-ID manuell (z.B. 3)" type="number" style="flex:1">
      <button class="btn btn-ghost" style="width:auto;padding:10px 14px;" onclick="jobIdManuell()">OK</button>
    </div>
    <button class="btn btn-primary" onclick="weiterZuSchritt2()" id="btn-step2">Weiter</button>
  </div>
</div>

<!-- Schritt 2: Artikel scannen -->
<div class="step" id="step-2">
  <div class="card">
    <div class="card-title">2 · Artikel scannen</div>
    <div id="job-info" style="margin-bottom:12px;"></div>
    <div id="gebuchte-artikel" style="margin-bottom:12px;"></div>
    <div class="scan-area active" id="artikel-scan-area" onclick="startScan('artikel')">
      <span class="icon">⬡</span>
      Artikel-QR scannen
    </div>
    <video id="artikel-video" playsinline></video>
    <div style="display:flex;gap:8px;margin-bottom:4px;">
      <input id="sn-manual" placeholder="Seriennummer eingeben" style="flex:1">
      <button class="btn btn-ghost" style="width:auto;padding:10px 14px;" onclick="snManuell()">OK</button>
    </div>
    <div id="scan-liste" style="margin-top:4px;"></div>
    <div style="margin-top:12px;">
      <button class="btn btn-ghost" onclick="zuSchritt1()">‹ Zurück</button>
      <button class="btn btn-primary" id="btn-buchen" onclick="buchen()" disabled>Equipment buchen</button>
    </div>
  </div>
</div>

<!-- Schritt 3: Bestätigung -->
<div class="step" id="step-3">
  <div class="card">
    <div class="card-title">3 · Gebucht ✓</div>
    <div id="bestaetigung" style="font-size:13px;line-height:1.8;"></div>
    <div style="margin-top:16px;">
      <button class="btn btn-ghost" onclick="neuerScan()">Weiteres Equipment buchen</button>
    </div>
  </div>
</div>

<div id="toast"></div>

<script src="https://cdn.jsdelivr.net/npm/jsqr@1.4.0/dist/jsQR.js"></script>
<script>
const API = '/api/v1';
let aktiverJob = null;
let scanListe = [];  // {{artikel_id, name, sn, menge}}
let scanMode = null;
let scanStream = null;
let scanInterval = null;

function toast(msg, err=false) {{
  const t = document.getElementById('toast');
  t.textContent = msg; t.className = 'show' + (err ? ' error' : '');
  setTimeout(() => t.className = '', 3000);
}}

function setProgress(step) {{
  [1,2,3].forEach(i => {{
    const d = document.getElementById('dot-' + i);
    d.className = 'progress-dot' + (i < step ? ' done' : i === step ? ' active' : '');
  }});
  document.querySelectorAll('.step').forEach(s => s.classList.remove('active'));
  document.getElementById('step-' + step).classList.add('active');
}}

// ── Scan ──────────────────────────────────────────────────────
async function startScan(mode) {{
  scanMode = mode;
  const videoId = mode + '-video';
  const video = document.getElementById(videoId);
  const area = document.getElementById(mode + '-scan-area');

  if (scanStream) stopScan();

  try {{
    scanStream = await navigator.mediaDevices.getUserMedia({{
      video: {{ facingMode: 'environment' }}
    }});
    video.srcObject = scanStream;
    video.classList.add('active');
    area.style.display = 'none';
    await video.play();

    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');
    scanInterval = setInterval(() => {{
      if (video.readyState === video.HAVE_ENOUGH_DATA) {{
        canvas.width = video.videoWidth;
        canvas.height = video.videoHeight;
        ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
        const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
        const code = jsQR(imageData.data, imageData.width, imageData.height);
        if (code) {{
          stopScan();
          video.classList.remove('active');
          area.style.display = 'block';
          handleQR(code.data, mode);
        }}
      }}
    }}, 200);
  }} catch(e) {{
    toast('Kamera nicht verfügbar: ' + e.message, true);
  }}
}}

function stopScan() {{
  if (scanInterval) {{ clearInterval(scanInterval); scanInterval = null; }}
  if (scanStream) {{ scanStream.getTracks().forEach(t => t.stop()); scanStream = null; }}
}}

// ── QR verarbeiten ────────────────────────────────────────────
async function handleQR(data, mode) {{
  if (mode === 'job') {{
    // Format: JOB:42
    const m = data.match(/^JOB:(\d+)$/);
    if (m) {{
      document.getElementById('job-select').value = m[1];
      toast('Job gescannt ✓');
    }} else {{
      toast('Kein gültiger Job-QR: ' + data, true);
    }}
  }} else if (mode === 'artikel') {{
    // Format: SN:XLR5-002-007 oder nur die SN direkt
    let sn = data.startsWith('SN:') ? data.split('|')[0].replace('SN:', '') : data;
    await addArtikelBySN(sn);
  }}
}}

async function addArtikelBySN(sn) {{
  try {{
    const e = await fetch(API + '/einheiten/sn/' + encodeURIComponent(sn)).then(r => {{
      if (!r.ok) throw new Error('Seriennummer nicht gefunden');
      return r.json();
    }});
    const artikel = await fetch(API + '/artikel/' + e.artikel_id).then(r => r.json());

    // Bereits in Liste?
    const existing = scanListe.find(x => x.artikel_id === artikel.id);
    if (existing) {{
      existing.menge++;
      toast(artikel.name + ' +1');
    }} else {{
      scanListe.push({{ artikel_id: artikel.id, name: artikel.name, sn: sn, menge: 1, verfuegbar: artikel.menge_verfuegbar }});
      toast(artikel.name + ' hinzugefügt ✓');
    }}
    renderListe();
  }} catch(e) {{
    toast(e.message, true);
  }}
}}

function renderListe() {{
  const el = document.getElementById('scan-liste');
  if (!scanListe.length) {{
    el.innerHTML = '';
    document.getElementById('btn-buchen').disabled = true;
    return;
  }}
  el.innerHTML = scanListe.map((item, i) => `
    <div class="item-row">
      <div>
        <div class="item-name">${{item.name}}</div>
        <div class="item-sn">${{item.sn}}</div>
      </div>
      <div style="display:flex;align-items:center;gap:8px;">
        <div class="item-menge">
          <button onclick="mengeAendern(${{i}}, -1)">−</button>
          <span>${{item.menge}}</span>
          <button onclick="mengeAendern(${{i}}, 1)">+</button>
        </div>
        <button class="remove-btn" onclick="entfernen(${{i}})">✕</button>
      </div>
    </div>`).join('');
  document.getElementById('btn-buchen').disabled = false;
}}

function mengeAendern(i, delta) {{
  scanListe[i].menge = Math.max(1, Math.min(scanListe[i].verfuegbar, scanListe[i].menge + delta));
  renderListe();
}}

function entfernen(i) {{
  scanListe.splice(i, 1);
  renderListe();
}}

// ── Navigation ────────────────────────────────────────────────
async function weiterZuSchritt2() {{
  const jobId = +document.getElementById('job-select').value;
  if (!jobId) {{ toast('Bitte Job auswählen', true); return; }}
  const sel = document.getElementById('job-select');
  const jobName = sel.options[sel.selectedIndex].text;
  aktiverJob = {{ id: jobId, name: jobName }};
  document.getElementById('job-info').innerHTML =
    `<span class="badge badge-job">Job: ${{jobName}}</span>`;
  setProgress(2);
  ladeGebuchteArtikel(jobId);
}}

async function ladeGebuchteArtikel(jobId) {{
  const el = document.getElementById('gebuchte-artikel');
  el.innerHTML = '<div style="color:var(--muted);font-size:11px;">Lade gebuchte Artikel…</div>';
  try {{
    const aus = await fetch(API + '/ausleihen/?job_id=' + jobId + '&nur_aktiv=true').then(r => r.json());
    if (!aus.length) {{
      el.innerHTML = '<div style="color:var(--muted);font-size:11px;border-left:2px solid var(--b);padding-left:8px;">Noch keine Artikel gebucht.</div>';
      return;
    }}
    // Artikelnamen laden
    const ids = [...new Set(aus.filter(a => a.artikel_id).map(a => a.artikel_id))];
    const artikelMap = {{}};
    await Promise.all(ids.map(id =>
      fetch(API + '/artikel/' + id).then(r => r.json()).then(a => artikelMap[id] = a).catch(() => {{}})
    ));
    el.innerHTML = `
      <div style="font-size:9px;letter-spacing:.15em;text-transform:uppercase;color:var(--muted);margin-bottom:8px;">Bereits gebucht</div>
      ${{aus.map(a => {{
        const art = artikelMap[a.artikel_id];
        return `<div style="display:flex;justify-content:space-between;align-items:center;padding:7px 0;border-bottom:1px solid var(--b);">
          <div>
            <div style="font-size:12px">${{art ? art.name : '#' + a.artikel_id}}</div>
            <div style="font-size:10px;color:var(--muted)">${{a.entleiher_name}}</div>
          </div>
          <div style="display:flex;align-items:center;gap:10px;">
            <span style="font-weight:bold">${{a.menge}}×</span>
            <button onclick="rueckgabeInScan(${{a.id}})" style="background:transparent;border:1px solid rgba(64,240,160,.3);color:var(--acc2);font-family:var(--font);font-size:10px;padding:4px 8px;cursor:pointer;">↩ Zurück</button>
          </div>
        </div>`;
      }}).join('')}}
      <div style="font-size:10px;color:var(--muted);margin-top:6px;">${{aus.reduce((s,a)=>s+a.menge,0)}} Stück gebucht</div>
    `;
  }} catch(e) {{
    el.innerHTML = '<div style="color:var(--danger);font-size:11px;">Fehler beim Laden</div>';
  }}
}}

async function rueckgabeInScan(id) {{
  try {{
    await fetch(API + '/ausleihen/' + id + '/rueckgabe', {{method: 'POST'}});
    toast('Rückgabe gebucht ✓');
    ladeGebuchteArtikel(aktiverJob.id);
  }} catch(e) {{ toast('Fehler', true); }}
}}

function zuSchritt1() {{
  stopScan();
  aktiverJob = null;
  setProgress(1);
}}

// ── Buchen ────────────────────────────────────────────────────
async function buchen() {{
  if (!aktiverJob || !scanListe.length) return;
  const btn = document.getElementById('btn-buchen');
  btn.disabled = true;
  btn.textContent = 'Buche...';

  const ergebnisse = [];
  for (const item of scanListe) {{
    try {{
      const r = await fetch(API + '/scan/buchen', {{
        method: 'POST',
        headers: {{'Content-Type': 'application/json'}},
        body: JSON.stringify({{
          job_id: aktiverJob.id,
          artikel_id: item.artikel_id,
          entleiher_name: aktiverJob.name,
          menge: item.menge,
        }})
      }});
      const d = await r.json();
      if (!r.ok) throw new Error(d.detail || 'Fehler');
      ergebnisse.push(`<div style="color:var(--acc2)">✓ ${{item.name}} × ${{item.menge}}</div>`);
    }} catch(e) {{
      ergebnisse.push(`<div style="color:var(--danger)">✕ ${{item.name}}: ${{e.message}}</div>`);
    }}
  }}

  document.getElementById('bestaetigung').innerHTML = `
    <div style="margin-bottom:10px;"><span class="badge badge-job">Job: ${{aktiverJob.name}}</span></div>
    ${{ergebnisse.join('')}}`;
  scanListe = [];
  setProgress(3);
}}

function neuerScan() {{
  scanListe = [];
  renderListe();
  setProgress(2);
}}

function jobIdManuell() {{
  const val = document.getElementById('job-id-manual').value.trim();
  if (val) {{
    document.getElementById('job-select').value = val;
    toast('Job-ID ' + val + ' gesetzt');
  }}
}}

function snManuell() {{
  const sn = document.getElementById('sn-manual').value.trim();
  if (sn) {{
    addArtikelBySN(sn);
    document.getElementById('sn-manual').value = '';
  }}
}}
</script>
</body>
</html>""")