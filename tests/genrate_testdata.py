"""
VT Inventory Generator – erzeugt realistische Testdaten für .vtinv Import.
Verwendung: python generate_vtinv.py
"""
import json
import random
from datetime import datetime, timedelta, date

random.seed(42)  # Reproduzierbare Daten


# ── Hilfsfunktionen ───────────────────────────────────────────

def rnd_date(start="2018-01-01", end="2025-12-31") -> str:
    s = date.fromisoformat(start)
    e = date.fromisoformat(end)
    return (s + timedelta(days=random.randint(0, (e - s).days))).isoformat()

def ts() -> str:
    return datetime.now().isoformat()

def zustand_gewichtet(alt=False) -> str:
    if alt:
        return random.choices(
            ["gut", "gut", "gebraucht", "beschaedigt", "reparatur"],
            weights=[2, 3, 3, 1, 1]
        )[0]
    return random.choices(
        ["neu", "gut", "gut", "gebraucht"],
        weights=[1, 4, 4, 1]
    )[0]


# ── Artikel-Definitionen ──────────────────────────────────────
# Jeder Eintrag: name, sn_prefix, kategorie, lagerorte, mengen, felder

ARTIKEL_TYPEN = [

    # ── Audio: Kabel ─────────────────────────────────────────
    {
        "name": "XLR Kabel 3m", "sn_prefix": "XLR3",
        "kategorie": "Audio", "lagerort": "Kabelregal A",
        "menge": (8, 20), "wert": (8, 18),
        "felder": {"laenge_m": 3, "stecker_a": "XLR-M", "stecker_b": "XLR-F",
                   "kabeltyp": "symmetrisch", "anzahl_kanaele": 1,
                   "hersteller": "Cordial", "farbe": "schwarz"}
    },
    {
        "name": "XLR Kabel 5m", "sn_prefix": "XLR5",
        "kategorie": "Audio", "lagerort": "Kabelregal A",
        "menge": (10, 25), "wert": (10, 22),
        "felder": {"laenge_m": 5, "stecker_a": "XLR-M", "stecker_b": "XLR-F",
                   "kabeltyp": "symmetrisch", "anzahl_kanaele": 1,
                   "hersteller": "Cordial", "farbe": "schwarz"}
    },
    {
        "name": "XLR Kabel 10m", "sn_prefix": "XLR10",
        "kategorie": "Audio", "lagerort": "Kabelregal A",
        "menge": (6, 15), "wert": (14, 28),
        "felder": {"laenge_m": 10, "stecker_a": "XLR-M", "stecker_b": "XLR-F",
                   "kabeltyp": "symmetrisch", "anzahl_kanaele": 1,
                   "hersteller": "Sommer Cable", "farbe": "schwarz"}
    },
    {
        "name": "XLR Kabel 20m", "sn_prefix": "XLR20",
        "kategorie": "Audio", "lagerort": "Kabelregal A",
        "menge": (4, 10), "wert": (20, 40),
        "felder": {"laenge_m": 20, "stecker_a": "XLR-M", "stecker_b": "XLR-F",
                   "kabeltyp": "symmetrisch", "anzahl_kanaele": 1,
                   "hersteller": "Sommer Cable", "farbe": "schwarz"}
    },
    {
        "name": "Klinke 6.3mm Kabel 3m", "sn_prefix": "KLK3",
        "kategorie": "Audio", "lagerort": "Kabelregal A",
        "menge": (4, 12), "wert": (6, 14),
        "felder": {"laenge_m": 3, "stecker_a": "Klinke 6.3mm TRS", "stecker_b": "Klinke 6.3mm TRS",
                   "kabeltyp": "symmetrisch", "anzahl_kanaele": 1,
                   "hersteller": "Cordial", "farbe": "schwarz"}
    },
    {
        "name": "Klinke 6.3mm auf XLR Adapter", "sn_prefix": "KXA",
        "kategorie": "Audio", "lagerort": "Adapterbox",
        "menge": (4, 10), "wert": (5, 12),
        "felder": {"stecker_a": "Klinke 6.3mm TS", "stecker_b": "XLR-F",
                   "ist_adapter": True, "kabeltyp": "unsymmetrisch",
                   "hersteller": "Neutrik", "farbe": "schwarz"}
    },
    {
        "name": "XLR auf Klinke 6.3mm Adapter", "sn_prefix": "XKA",
        "kategorie": "Audio", "lagerort": "Adapterbox",
        "menge": (4, 10), "wert": (5, 12),
        "felder": {"stecker_a": "XLR-M", "stecker_b": "Klinke 6.3mm TS",
                   "ist_adapter": True, "kabeltyp": "unsymmetrisch",
                   "hersteller": "Neutrik", "farbe": "schwarz"}
    },
    {
        "name": "Cinch Stereo Kabel 1m", "sn_prefix": "CIN1",
        "kategorie": "Audio", "lagerort": "Kabelregal A",
        "menge": (3, 8), "wert": (4, 10),
        "felder": {"laenge_m": 1, "stecker_a": "Cinch (RCA)", "stecker_b": "Cinch (RCA)",
                   "kabeltyp": "unsymmetrisch", "anzahl_kanaele": 2,
                   "hersteller": "Cordial", "farbe": "schwarz/rot"}
    },
    {
        "name": "Speakon Lautsprecherkabel 5m", "sn_prefix": "SPK5",
        "kategorie": "Audio", "lagerort": "Kabelregal B",
        "menge": (4, 12), "wert": (12, 25),
        "felder": {"laenge_m": 5, "stecker_a": "Speakon NL4", "stecker_b": "Speakon NL4",
                   "kabeltyp": "unsymmetrisch", "anzahl_kanaele": 1, "impedanz_ohm": 4,
                   "hersteller": "Cordial", "farbe": "schwarz"}
    },
    {
        "name": "Speakon Lautsprecherkabel 10m", "sn_prefix": "SPK10",
        "kategorie": "Audio", "lagerort": "Kabelregal B",
        "menge": (3, 8), "wert": (18, 35),
        "felder": {"laenge_m": 10, "stecker_a": "Speakon NL4", "stecker_b": "Speakon NL4",
                   "kabeltyp": "unsymmetrisch", "anzahl_kanaele": 1, "impedanz_ohm": 4,
                   "hersteller": "Cordial", "farbe": "schwarz"}
    },
    {
        "name": "Multicore 12/4 30m", "sn_prefix": "MC12",
        "kategorie": "Audio", "lagerort": "Stagebox-Lager",
        "menge": (1, 3), "wert": (180, 350),
        "felder": {"laenge_m": 30, "stecker_a": "Multipin", "stecker_b": "XLR-M/F",
                   "kabeltyp": "symmetrisch", "anzahl_kanaele": 16,
                   "hersteller": "Sommer Cable", "farbe": "grau"}
    },

    # ── Audio: Geräte ─────────────────────────────────────────
    {
        "name": "DI-Box passiv", "sn_prefix": "DIP",
        "kategorie": "Audio", "lagerort": "Audiokoffer",
        "menge": (4, 10), "wert": (25, 60),
        "felder": {"stecker_a": "Klinke 6.3mm", "stecker_b": "XLR-M",
                   "ist_adapter": True, "impedanz_ohm": 10000,
                   "hersteller": "the t.bone", "farbe": "schwarz"}
    },
    {
        "name": "DI-Box aktiv", "sn_prefix": "DIA",
        "kategorie": "Audio", "lagerort": "Audiokoffer",
        "menge": (2, 6), "wert": (60, 150),
        "felder": {"stecker_a": "Klinke 6.3mm", "stecker_b": "XLR-M",
                   "ist_adapter": True, "spannung_v": 48,
                   "hersteller": "Radial", "farbe": "schwarz"}
    },
    {
        "name": "Stagebox 16/4", "sn_prefix": "SB16",
        "kategorie": "Audio", "lagerort": "Stagebox-Lager",
        "menge": (1, 3), "wert": (200, 450),
        "felder": {"anzahl_kanaele": 20, "stecker_a": "XLR", "stecker_b": "Multipin",
                   "hersteller": "Adam Hall", "farbe": "schwarz",
                   "wartungshinweis": "Buchsen jährlich auf Korrosion prüfen"}
    },
    {
        "name": "Mikrofon Stativ groß", "sn_prefix": "MST",
        "kategorie": "Zubehör", "lagerort": "Stativlager",
        "menge": (6, 15), "wert": (20, 45),
        "felder": {"gewicht_kg": 2.4, "hersteller": "König & Meyer", "farbe": "schwarz"}
    },
    {
        "name": "Mikrofon Tischstativ", "sn_prefix": "MTS",
        "kategorie": "Zubehör", "lagerort": "Stativlager",
        "menge": (4, 10), "wert": (8, 20),
        "felder": {"gewicht_kg": 0.6, "hersteller": "König & Meyer", "farbe": "schwarz"}
    },

    # ── Licht ─────────────────────────────────────────────────
    {
        "name": "DMX Kabel 3m", "sn_prefix": "DMX3",
        "kategorie": "Licht", "lagerort": "Kabelregal B",
        "menge": (8, 20), "wert": (6, 14),
        "felder": {"laenge_m": 3, "stecker_a": "XLR-M 5-pol", "stecker_b": "XLR-F 5-pol",
                   "kabeltyp": "digital", "anzahl_kanaele": 1, "impedanz_ohm": 110,
                   "hersteller": "Cordial", "farbe": "schwarz"}
    },
    {
        "name": "DMX Kabel 5m", "sn_prefix": "DMX5",
        "kategorie": "Licht", "lagerort": "Kabelregal B",
        "menge": (6, 16), "wert": (8, 18),
        "felder": {"laenge_m": 5, "stecker_a": "XLR-M 5-pol", "stecker_b": "XLR-F 5-pol",
                   "kabeltyp": "digital", "anzahl_kanaele": 1, "impedanz_ohm": 110,
                   "hersteller": "Cordial", "farbe": "schwarz"}
    },
    {
        "name": "DMX Kabel 10m", "sn_prefix": "DMX10",
        "kategorie": "Licht", "lagerort": "Kabelregal B",
        "menge": (4, 10), "wert": (12, 24),
        "felder": {"laenge_m": 10, "stecker_a": "XLR-M 5-pol", "stecker_b": "XLR-F 5-pol",
                   "kabeltyp": "digital", "anzahl_kanaele": 1, "impedanz_ohm": 110,
                   "hersteller": "Sommer Cable", "farbe": "schwarz"}
    },
    {
        "name": "DMX 3-pol auf 5-pol Adapter", "sn_prefix": "D35",
        "kategorie": "Licht", "lagerort": "Adapterbox",
        "menge": (4, 8), "wert": (6, 12),
        "felder": {"stecker_a": "XLR-M 3-pol", "stecker_b": "XLR-F 5-pol",
                   "ist_adapter": True, "kabeltyp": "digital",
                   "hersteller": "Neutrik", "farbe": "schwarz"}
    },
    {
        "name": "LED PAR Scheinwerfer RGBW", "sn_prefix": "PAR",
        "kategorie": "Licht", "lagerort": "Lichtcase",
        "menge": (4, 12), "wert": (60, 150),
        "felder": {"leistung_w": 36, "spannung_v": 230, "schutzklasse_ip": "IP20",
                   "gewicht_kg": 1.8, "hersteller": "Cameo", "farbe": "schwarz",
                   "wartungshinweis": "LED-Modul nach 50.000h tauschen"}
    },
    {
        "name": "LED Moving Head Spot", "sn_prefix": "MHD",
        "kategorie": "Licht", "lagerort": "Lichtcase",
        "menge": (2, 6), "wert": (300, 800),
        "felder": {"leistung_w": 60, "spannung_v": 230, "schutzklasse_ip": "IP20",
                   "gewicht_kg": 5.5, "hersteller": "Cameo", "farbe": "weiß",
                   "wartungshinweis": "Gobos halbjährlich prüfen, Lüfter reinigen"}
    },
    {
        "name": "Followspot 150W", "sn_prefix": "FSP",
        "kategorie": "Licht", "lagerort": "Lichtcase",
        "menge": (1, 2), "wert": (400, 900),
        "felder": {"leistung_w": 150, "spannung_v": 230,
                   "gewicht_kg": 8.2, "hersteller": "Eurolite", "farbe": "schwarz",
                   "wartungshinweis": "Lampe nach 750h tauschen"}
    },
    {
        "name": "Lichtstativ groß", "sn_prefix": "LST",
        "kategorie": "Licht", "lagerort": "Stativlager",
        "menge": (4, 8), "wert": (35, 80),
        "felder": {"gewicht_kg": 4.5, "hersteller": "Adam Hall", "farbe": "schwarz"}
    },

    # ── Strom ─────────────────────────────────────────────────
    {
        "name": "Schuko Verlängerung 10m", "sn_prefix": "SCH10",
        "kategorie": "Strom", "lagerort": "Stromkiste",
        "menge": (4, 12), "wert": (15, 30),
        "felder": {"laenge_m": 10, "stecker_a": "Schuko", "stecker_b": "Schuko-Kupplung",
                   "spannung_v": 230, "leistung_w": 3500, "schutzklasse_ip": "IP20",
                   "hersteller": "Brennenstuhl", "farbe": "schwarz"}
    },
    {
        "name": "Schuko Verlängerung 20m", "sn_prefix": "SCH20",
        "kategorie": "Strom", "lagerort": "Stromkiste",
        "menge": (3, 8), "wert": (25, 45),
        "felder": {"laenge_m": 20, "stecker_a": "Schuko", "stecker_b": "Schuko-Kupplung",
                   "spannung_v": 230, "leistung_w": 3500, "schutzklasse_ip": "IP20",
                   "hersteller": "Brennenstuhl", "farbe": "orange"}
    },
    {
        "name": "PowerCON Kabel 2m", "sn_prefix": "PWC2",
        "kategorie": "Strom", "lagerort": "Stromkiste",
        "menge": (6, 16), "wert": (12, 22),
        "felder": {"laenge_m": 2, "stecker_a": "PowerCON TRUE1", "stecker_b": "PowerCON TRUE1",
                   "spannung_v": 230, "leistung_w": 2300, "schutzklasse_ip": "IP65",
                   "hersteller": "Adam Hall", "farbe": "schwarz"}
    },
    {
        "name": "PowerCON Kabel 5m", "sn_prefix": "PWC5",
        "kategorie": "Strom", "lagerort": "Stromkiste",
        "menge": (4, 12), "wert": (16, 30),
        "felder": {"laenge_m": 5, "stecker_a": "PowerCON TRUE1", "stecker_b": "PowerCON TRUE1",
                   "spannung_v": 230, "leistung_w": 2300, "schutzklasse_ip": "IP65",
                   "hersteller": "Adam Hall", "farbe": "schwarz"}
    },
    {
        "name": "PowerCON auf Schuko Adapter", "sn_prefix": "PSA",
        "kategorie": "Strom", "lagerort": "Adapterbox",
        "menge": (4, 8), "wert": (10, 20),
        "felder": {"stecker_a": "PowerCON TRUE1", "stecker_b": "Schuko-Kupplung",
                   "ist_adapter": True, "spannung_v": 230, "leistung_w": 2300,
                   "hersteller": "Neutrik", "farbe": "schwarz"}
    },
    {
        "name": "CEE 16A Verlängerung 10m", "sn_prefix": "CEE10",
        "kategorie": "Strom", "lagerort": "Stromkiste",
        "menge": (2, 5), "wert": (35, 70),
        "felder": {"laenge_m": 10, "stecker_a": "CEE 16A 5-pol", "stecker_b": "CEE 16A 5-pol",
                   "spannung_v": 400, "leistung_w": 11000, "schutzklasse_ip": "IP44",
                   "hersteller": "PCE", "farbe": "blau"}
    },
    {
        "name": "Verteilerdose 6-fach", "sn_prefix": "VTL",
        "kategorie": "Strom", "lagerort": "Stromkiste",
        "menge": (2, 6), "wert": (20, 45),
        "felder": {"stecker_a": "Schuko", "stecker_b": "6x Schuko",
                   "spannung_v": 230, "leistung_w": 3500,
                   "hersteller": "Brennenstuhl", "farbe": "schwarz",
                   "wartungshinweis": "Sicherung bei Defekt prüfen"}
    },

    # ── Video ─────────────────────────────────────────────────
    {
        "name": "HDMI Kabel 2m", "sn_prefix": "HDM2",
        "kategorie": "Video", "lagerort": "Videokiste",
        "menge": (4, 10), "wert": (8, 18),
        "felder": {"laenge_m": 2, "stecker_a": "HDMI-A", "stecker_b": "HDMI-A",
                   "kabeltyp": "digital", "hersteller": "Delock", "farbe": "schwarz"}
    },
    {
        "name": "HDMI Kabel 5m", "sn_prefix": "HDM5",
        "kategorie": "Video", "lagerort": "Videokiste",
        "menge": (3, 8), "wert": (12, 25),
        "felder": {"laenge_m": 5, "stecker_a": "HDMI-A", "stecker_b": "HDMI-A",
                   "kabeltyp": "digital", "hersteller": "Delock", "farbe": "schwarz"}
    },
    {
        "name": "HDMI auf DisplayPort Adapter", "sn_prefix": "HDA",
        "kategorie": "Video", "lagerort": "Adapterbox",
        "menge": (2, 6), "wert": (10, 20),
        "felder": {"stecker_a": "HDMI-A", "stecker_b": "DisplayPort",
                   "ist_adapter": True, "kabeltyp": "digital",
                   "hersteller": "Delock", "farbe": "schwarz"}
    },
    {
        "name": "VGA Kabel 5m", "sn_prefix": "VGA5",
        "kategorie": "Video", "lagerort": "Videokiste",
        "menge": (2, 6), "wert": (6, 14),
        "felder": {"laenge_m": 5, "stecker_a": "VGA-M", "stecker_b": "VGA-M",
                   "kabeltyp": "analog", "hersteller": "Delock", "farbe": "schwarz"}
    },

    # ── Netzwerk ──────────────────────────────────────────────
    {
        "name": "LAN Kabel Cat6 5m", "sn_prefix": "LAN5",
        "kategorie": "Netzwerk", "lagerort": "Netzwerkbox",
        "menge": (6, 20), "wert": (4, 10),
        "felder": {"laenge_m": 5, "stecker_a": "RJ45", "stecker_b": "RJ45",
                   "kabeltyp": "digital", "anzahl_kanaele": 8,
                   "hersteller": "Delock", "farbe": "blau"}
    },
    {
        "name": "LAN Kabel Cat6 10m", "sn_prefix": "LAN10",
        "kategorie": "Netzwerk", "lagerort": "Netzwerkbox",
        "menge": (4, 12), "wert": (6, 14),
        "felder": {"laenge_m": 10, "stecker_a": "RJ45", "stecker_b": "RJ45",
                   "kabeltyp": "digital", "anzahl_kanaele": 8,
                   "hersteller": "Delock", "farbe": "blau"}
    },
    {
        "name": "LAN Kabel Cat6 20m", "sn_prefix": "LAN20",
        "kategorie": "Netzwerk", "lagerort": "Netzwerkbox",
        "menge": (2, 6), "wert": (10, 22),
        "felder": {"laenge_m": 20, "stecker_a": "RJ45", "stecker_b": "RJ45",
                   "kabeltyp": "digital", "anzahl_kanaele": 8,
                   "hersteller": "Delock", "farbe": "blau"}
    },
    {
        "name": "Network Switch 8-Port", "sn_prefix": "NSW",
        "kategorie": "Netzwerk", "lagerort": "Netzwerkbox",
        "menge": (1, 3), "wert": (30, 80),
        "felder": {"spannung_v": 12, "leistung_w": 15, "anzahl_kanaele": 8,
                   "hersteller": "TP-Link", "farbe": "schwarz"}
    },

    # ── Cases & Transport ─────────────────────────────────────
    {
        "name": "Flightcase 19 Zoll 4HE", "sn_prefix": "FC4",
        "kategorie": "Transport", "lagerort": "Stativlager",
        "menge": (2, 5), "wert": (150, 350),
        "felder": {"gewicht_kg": 8.5, "schutzklasse_ip": "IP54",
                   "hersteller": "Adam Hall", "farbe": "schwarz"}
    },
    {
        "name": "Kabelkoffer groß", "sn_prefix": "KKG",
        "kategorie": "Transport", "lagerort": "Stativlager",
        "menge": (2, 4), "wert": (60, 120),
        "felder": {"gewicht_kg": 3.2, "hersteller": "Zarges", "farbe": "schwarz"}
    },
]


# ── Generator ─────────────────────────────────────────────────

def generate_artikel(artikel_id: int, typ: dict) -> dict:
    menge = random.randint(*typ["menge"])
    # Realistische Verfügbarkeit: meist gut, manchmal knapp
    ausgeliehen = random.choices(
        [0, 1, 2, int(menge * 0.3), int(menge * 0.5)],
        weights=[4, 3, 2, 1, 1]
    )[0]
    ausgeliehen = min(ausgeliehen, menge)
    verfuegbar = menge - ausgeliehen

    kaufdatum = rnd_date("2018-01-01", "2024-12-31")
    garantie_monate = random.choice([12, 24, 36])
    kauf_d = date.fromisoformat(kaufdatum)
    garantie = (kauf_d + timedelta(days=garantie_monate * 30)).isoformat()

    wert = round(random.uniform(*typ["wert"]), 2)

    artikel = {
        "id": artikel_id,
        "name": typ["name"],
        "seriennummer": None,
        "beschreibung": None,
        "menge_gesamt": menge,
        "menge_verfuegbar": verfuegbar,
        "zustand": zustand_gewichtet(alt=(kauf_d.year < 2022)),
        "lagerort": typ["lagerort"],
        "anschaffungswert": wert,
        "laenge_m": None,
        "stecker_a": None,
        "stecker_b": None,
        "ist_adapter": False,
        "leistung_w": None,
        "spannung_v": None,
        "impedanz_ohm": None,
        "kabeltyp": None,
        "anzahl_kanaele": None,
        "schutzklasse_ip": None,
        "gewicht_kg": None,
        "hersteller": None,
        "modell": None,
        "farbe": None,
        "kaufdatum": kaufdatum,
        "garantie_bis": garantie,
        "wartungshinweis": None,
        "erstellt_am": ts(),
        "aktualisiert_am": ts(),
        "kategorie": typ["kategorie"],
        "einheiten": [],
    }

    # Felder aus Template übernehmen
    for k, v in typ["felder"].items():
        artikel[k] = v

    # Einheiten mit realistischen Seriennummern
    prefix = typ["sn_prefix"]
    for i in range(menge):
        einheit_zustand = zustand_gewichtet(alt=(kauf_d.year < 2022))
        notiz = None
        if einheit_zustand == "beschaedigt":
            notiz = random.choice([
                "Stecker leicht verbogen",
                "Isolierung angebrochen",
                "Buchse wackelt",
                "Knick am Stecker",
                "Kontaktkorrosion",
            ])
        elif einheit_zustand == "reparatur":
            notiz = random.choice([
                "Zur Reparatur bei Techniker",
                "Stecker muss gelötet werden",
                "Wartet auf Ersatzteil",
            ])
        artikel["einheiten"].append({
            "seriennummer": f"{prefix}-{artikel_id:03d}-{i+1:03d}",
            "zustand": einheit_zustand,
            "notizen": notiz,
        })

    return artikel


def generate_inventory(seed: int = 42) -> dict:
    random.seed(seed)
    artikel_liste = []
    for i, typ in enumerate(ARTIKEL_TYPEN):
        artikel = generate_artikel(i + 1, typ)
        artikel_liste.append(artikel)

    return {
        "__vtinv__": "1.0",
        "erstellt_am": ts(),
        "quelle": "VT-Generator",
        "anzahl": len(artikel_liste),
        "artikel": artikel_liste,
    }


if __name__ == "__main__":
    data = generate_inventory()
    dateiname = "vt_inventory_realistisch.vtinv"
    with open(dateiname, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    total_einheiten = sum(len(a["einheiten"]) for a in data["artikel"])
    total_menge = sum(a["menge_gesamt"] for a in data["artikel"])
    print(f"✓ {dateiname} erstellt")
    print(f"  {len(data['artikel'])} Artikel-Typen")
    print(f"  {total_menge} Stück gesamt")
    print(f"  {total_einheiten} Einheiten mit Seriennummern")
    print(f"  Kategorien: {', '.join(sorted(set(a['kategorie'] for a in data['artikel'])))}")
