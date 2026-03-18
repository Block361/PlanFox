# Veranstaltungstechnik Inventarsystem

Inventarverwaltung für Veranstaltungstechnik (Kabel, Cases, Lautsprecher, …)  
mit FastAPI, PostgreSQL, CLI und Export-Funktion.

## Schnellstart

### 1. Abhängigkeiten installieren
```bash
pip install -r requirements.txt
```

### 2. Umgebungsvariablen konfigurieren
```bash
cp .env.example .env
# .env anpassen (DATABASE_URL, SECRET_KEY)
```

### 3. Datenbank initialisieren
```bash
# Option A: via CLI
python -m cli.main init-db

# Option B: via Alembic (produktiv empfohlen)
alembic init migrations
alembic revision --autogenerate -m "initial"
alembic upgrade head
```

### 4. Server starten
```bash
uvicorn app.main:app --reload
```
API-Docs: http://localhost:8000/docs

---

## CLI-Befehle

```bash
# Artikel
python -m cli.main artikel liste
python -m cli.main artikel liste --suche "Kabel" --verfuegbar
python -m cli.main artikel neu
python -m cli.main artikel export --format csv -o inventar.csv
python -m cli.main artikel export --format pdf

# Ausleihe
python -m cli.main ausleihe liste --aktiv
python -m cli.main ausleihe neu
python -m cli.main ausleihe rueckgabe 42
```

---

## API-Endpunkte

| Methode | Pfad | Beschreibung |
|---|---|---|
| GET | /api/v1/artikel/ | Artikel auflisten (Filter: kategorie, zustand, suche) |
| POST | /api/v1/artikel/ | Artikel anlegen |
| PATCH | /api/v1/artikel/{id} | Artikel bearbeiten |
| DELETE | /api/v1/artikel/{id} | Artikel löschen |
| GET | /api/v1/artikel/export/csv | CSV-Export |
| GET | /api/v1/artikel/export/pdf | PDF-Export |
| GET | /api/v1/ausleihen/ | Ausleihen auflisten |
| POST | /api/v1/ausleihen/ | Neue Ausleihe |
| POST | /api/v1/ausleihen/{id}/rueckgabe | Rückgabe buchen |
| GET | /api/v1/jobs/ | Jobs auflisten |
| POST | /api/v1/jobs/ | Job anlegen |
| PATCH | /api/v1/jobs/{id} | Job bearbeiten |

---

## Tests ausführen
```bash
pytest tests/ -v
```

## Projektstruktur
```
inventar/
├── app/
│   ├── api/routers/     # FastAPI Router (artikel, ausleihe, jobs)
│   ├── models/          # SQLAlchemy-Modelle
│   ├── schemas/         # Pydantic-Schemas
│   ├── services/        # Business Logic + Export
│   ├── config.py        # Konfiguration (Settings)
│   ├── database.py      # DB-Session
│   └── main.py          # FastAPI App
├── cli/
│   └── main.py          # Click CLI-Tool
├── tests/
│   └── test_artikel.py
├── requirements.txt
└── .env.example
```
