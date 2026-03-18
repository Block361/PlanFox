import io
from datetime import datetime
from sqlalchemy.orm import Session
from app.models import Artikel, Ausleihe


def export_artikel_csv(db: Session) -> bytes:
    import pandas as pd

    artikel_list = db.query(Artikel).all()
    rows = [
        {
            "ID": a.id,
            "Name": a.name,
            "Seriennummer": a.seriennummer or "",
            "Kategorie": a.kategorie.name if a.kategorie else "",
            "Menge gesamt": a.menge_gesamt,
            "Menge verfügbar": a.menge_verfuegbar,
            "Zustand": a.zustand.value,
            "Lagerort": a.lagerort or "",
            "Anschaffungswert": a.anschaffungswert or "",
        }
        for a in artikel_list
    ]
    df = pd.DataFrame(rows)
    buf = io.BytesIO()
    df.to_csv(buf, index=False, encoding="utf-8-sig")
    return buf.getvalue()


def export_ausleihen_csv(db: Session, nur_aktiv: bool = False) -> bytes:
    import pandas as pd

    q = db.query(Ausleihe)
    if nur_aktiv:
        q = q.filter(Ausleihe.ist_aktiv == True)
    rows = [
        {
            "ID": a.id,
            "Artikel": a.artikel.name if a.artikel else a.artikel_id,
            "Entleiher": a.entleiher_name,
            "Kontakt": a.entleiher_kontakt or "",
            "Menge": a.menge,
            "Ausgeliehen am": a.ausgeliehen_am.strftime("%d.%m.%Y %H:%M"),
            "Rückgabe geplant": a.rueckgabe_geplant.strftime("%d.%m.%Y") if a.rueckgabe_geplant else "",
            "Zurückgegeben am": a.zurueckgegeben_am.strftime("%d.%m.%Y %H:%M") if a.zurueckgegeben_am else "",
            "Status": "Aktiv" if a.ist_aktiv else "Zurückgegeben",
        }
        for a in q.all()
    ]
    df = pd.DataFrame(rows)
    buf = io.BytesIO()
    df.to_csv(buf, index=False, encoding="utf-8-sig")
    return buf.getvalue()


def export_artikel_pdf(db: Session) -> bytes:
    from reportlab.lib.pagesizes import A4, landscape
    from reportlab.lib import colors
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
    from reportlab.lib.styles import getSampleStyleSheet

    artikel_list = db.query(Artikel).all()
    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=20, rightMargin=20)
    styles = getSampleStyleSheet()
    elements = []

    elements.append(Paragraph("Inventarliste – Veranstaltungstechnik", styles["Title"]))
    elements.append(Paragraph(f"Erstellt: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles["Normal"]))
    elements.append(Spacer(1, 12))

    header = ["ID", "Name", "Kategorie", "Gesamt", "Verfügbar", "Zustand", "Lagerort"]
    data = [header] + [
        [
            str(a.id),
            a.name,
            a.kategorie.name if a.kategorie else "–",
            str(a.menge_gesamt),
            str(a.menge_verfuegbar),
            a.zustand.value,
            a.lagerort or "–",
        ]
        for a in artikel_list
    ]

    table = Table(data, colWidths=[30, 180, 100, 50, 60, 70, 120])
    table.setStyle(
        TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#1D9E75")),
            ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
            ("FONTNAME", (0, 0), (-1, 0), "Helvetica-Bold"),
            ("FONTSIZE", (0, 0), (-1, -1), 9),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1EFE8")]),
            ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#B4B2A9")),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("PADDING", (0, 0), (-1, -1), 4),
        ])
    )
    elements.append(table)
    doc.build(elements)
    return buf.getvalue()
