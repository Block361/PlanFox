"""
VTInv – Veranstaltungstechnik Inventory Format (.vtinv)

Dateistruktur (JSON-basiert):
{
  "__vtinv__": "1.0",
  "erstellt_am": "2025-03-19T12:00:00",
  "quelle": "VT-Inventar",
  "artikel": [ { ... }, ... ]
}
"""
import json
from datetime import datetime, date
from typing import Any
from sqlalchemy.orm import Session
from app.models import Artikel, ArtikelEinheit, ArtikelZustand

VTINV_MAGIC = "__vtinv__"
VTINV_VERSION = "1.0"
VTINV_MIME = "application/x-vtinv"
VTINV_EXT = ".vtinv"

# Mapping externer Zustandswerte auf interne Enum-Werte
ZUSTAND_MAP = {
    "gut": ArtikelZustand.gut,
    "neu": ArtikelZustand.gut,
    "gebraucht": ArtikelZustand.gut,
    "ok": ArtikelZustand.gut,
    "good": ArtikelZustand.gut,
    "used": ArtikelZustand.gut,
    "beschaedigt": ArtikelZustand.beschaedigt,
    "beschädigt": ArtikelZustand.beschaedigt,
    "damaged": ArtikelZustand.beschaedigt,
    "defekt": ArtikelZustand.beschaedigt,
    "broken": ArtikelZustand.beschaedigt,
    "reparatur": ArtikelZustand.reparatur,
    "repair": ArtikelZustand.reparatur,
    "in reparatur": ArtikelZustand.reparatur,
    "ausgemustert": ArtikelZustand.ausgemustert,
    "retired": ArtikelZustand.ausgemustert,
    "alt": ArtikelZustand.ausgemustert,
}


def _parse_zustand(val: str | None) -> ArtikelZustand:
    if not val:
        return ArtikelZustand.gut
    return ZUSTAND_MAP.get(str(val).lower().strip(), ArtikelZustand.gut)


def _parse_date(val) -> date | None:
    if not val:
        return None
    try:
        return date.fromisoformat(str(val)[:10])
    except (ValueError, TypeError):
        return None


def _parse_float(val) -> float | None:
    try:
        return float(val) if val is not None else None
    except (ValueError, TypeError):
        return None


def _parse_int(val) -> int | None:
    try:
        return int(val) if val is not None else None
    except (ValueError, TypeError):
        return None


def _serialize(val: Any) -> Any:
    if isinstance(val, datetime):
        return val.isoformat()
    if isinstance(val, date):
        return val.isoformat()
    if isinstance(val, ArtikelZustand):
        return val.value
    return val


# ── Export ────────────────────────────────────────────────────

def artikel_zu_dict(artikel: Artikel) -> dict:
    felder = [
        "id", "name", "seriennummer", "beschreibung",
        "menge_gesamt", "menge_verfuegbar", "zustand", "lagerort",
        "anschaffungswert", "laenge_m", "stecker_a", "stecker_b",
        "ist_adapter", "leistung_w", "spannung_v", "impedanz_ohm",
        "kabeltyp", "anzahl_kanaele", "schutzklasse_ip", "gewicht_kg",
        "hersteller", "modell", "farbe", "kaufdatum", "garantie_bis",
        "wartungshinweis", "erstellt_am", "aktualisiert_am",
    ]
    d = {f: _serialize(getattr(artikel, f, None)) for f in felder}
    d["kategorie"] = artikel.kategorie.name if artikel.kategorie else None
    d["einheiten"] = [
        {
            "seriennummer": e.seriennummer,
            "zustand": e.zustand.value,
            "notizen": e.notizen,
        }
        for e in sorted(artikel.einheiten, key=lambda x: x.seriennummer)
    ]
    return d


def export_vtinv(db: Session, artikel_ids: list[int] | None = None) -> bytes:
    q = db.query(Artikel)
    if artikel_ids:
        q = q.filter(Artikel.id.in_(artikel_ids))
    artikel_liste = q.order_by(Artikel.id).all()
    payload = {
        VTINV_MAGIC: VTINV_VERSION,
        "erstellt_am": datetime.utcnow().isoformat(),
        "quelle": "VT-Inventar",
        "anzahl": len(artikel_liste),
        "artikel": [artikel_zu_dict(a) for a in artikel_liste],
    }
    return json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")


# ── Parser ────────────────────────────────────────────────────

class VtinvParseError(Exception):
    pass


def parse_vtinv(data: bytes) -> dict:
    try:
        payload = json.loads(data.decode("utf-8"))
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        raise VtinvParseError(f"Ungültiges Format: {e}")
    if VTINV_MAGIC not in payload:
        raise VtinvParseError("Keine gültige .vtinv Datei (Magic-Header fehlt)")
    if not payload[VTINV_MAGIC].startswith("1."):
        raise VtinvParseError(f"Nicht unterstützte Version: {payload[VTINV_MAGIC]}")
    if "artikel" not in payload or not isinstance(payload["artikel"], list):
        raise VtinvParseError("Pflichtfeld 'artikel' fehlt oder ungültig")
    return payload


# ── Import ────────────────────────────────────────────────────

def import_vtinv(db: Session, data: bytes, ueberschreiben: bool = False) -> dict:
    payload = parse_vtinv(data)
    artikel_liste = payload["artikel"]
    stats = {"neu": 0, "aktualisiert": 0, "uebersprungen": 0, "fehler": [], "artikel": []}

    for eintrag in artikel_liste:
        name = (eintrag.get("name") or "").strip()
        if not name:
            stats["fehler"].append("Eintrag ohne Name übersprungen")
            stats["uebersprungen"] += 1
            continue

        # Jeder Artikel in eigener Transaktion – Fehler isolieren
        try:
            existierend = db.query(Artikel).filter(Artikel.name == name).first()

            if existierend and not ueberschreiben:
                stats["uebersprungen"] += 1
                continue

            menge = _parse_int(eintrag.get("menge_gesamt")) or 1
            verfuegbar = _parse_int(eintrag.get("menge_verfuegbar"))
            if verfuegbar is None:
                verfuegbar = menge

            felder = dict(
                name=name,
                beschreibung=eintrag.get("beschreibung"),
                menge_gesamt=menge,
                menge_verfuegbar=verfuegbar,
                zustand=_parse_zustand(eintrag.get("zustand")),
                lagerort=eintrag.get("lagerort"),
                anschaffungswert=_parse_float(eintrag.get("anschaffungswert")),
                laenge_m=_parse_float(eintrag.get("laenge_m")),
                stecker_a=eintrag.get("stecker_a"),
                stecker_b=eintrag.get("stecker_b"),
                ist_adapter=bool(eintrag.get("ist_adapter", False)),
                leistung_w=_parse_float(eintrag.get("leistung_w")),
                spannung_v=_parse_float(eintrag.get("spannung_v")),
                impedanz_ohm=_parse_float(eintrag.get("impedanz_ohm")),
                kabeltyp=eintrag.get("kabeltyp"),
                anzahl_kanaele=_parse_int(eintrag.get("anzahl_kanaele")),
                schutzklasse_ip=eintrag.get("schutzklasse_ip"),
                gewicht_kg=_parse_float(eintrag.get("gewicht_kg")),
                hersteller=eintrag.get("hersteller"),
                modell=eintrag.get("modell"),
                farbe=eintrag.get("farbe"),
                kaufdatum=_parse_date(eintrag.get("kaufdatum")),
                garantie_bis=_parse_date(eintrag.get("garantie_bis")),
                wartungshinweis=eintrag.get("wartungshinweis"),
            )

            if existierend:
                for k, v in felder.items():
                    setattr(existierend, k, v)
                artikel = existierend
                stats["aktualisiert"] += 1
            else:
                artikel = Artikel(**felder)
                db.add(artikel)
                db.flush()  # ID vergeben ohne commit
                stats["neu"] += 1

            # Einheiten importieren
            for ed in eintrag.get("einheiten", []):
                sn = (ed.get("seriennummer") or "").strip()
                if not sn:
                    continue
                exists = db.query(ArtikelEinheit).filter(
                    ArtikelEinheit.seriennummer == sn
                ).first()
                if not exists:
                    db.add(ArtikelEinheit(
                        artikel_id=artikel.id,
                        seriennummer=sn,
                        zustand=_parse_zustand(ed.get("zustand")),
                        notizen=ed.get("notizen"),
                    ))

            # Einzel-Commit pro Artikel – kein Rollback aller anderen bei Fehler
            db.commit()
            stats["artikel"].append({"id": artikel.id, "name": name})

        except Exception as e:
            db.rollback()
            stats["fehler"].append(f"'{name}': {str(e)}")
            stats["uebersprungen"] += 1
            continue

    return stats