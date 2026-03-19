from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from app.config import settings
from app.api.routers import artikel, ausleihe, jobs, einheiten
from app.api.routers import io as io_router
from app.api.routers import scan

app = FastAPI(
    title=settings.app_name,
    description="REST-API für das Inventarsystem der Veranstaltungstechnik",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(artikel.router, prefix="/api/v1")
app.include_router(ausleihe.router, prefix="/api/v1")
app.include_router(jobs.router, prefix="/api/v1")
app.include_router(einheiten.router, prefix="/api/v1")
app.include_router(io_router.router, prefix="/api/v1")
app.include_router(scan.router, prefix="/api/v1")

_static = os.path.join(os.path.dirname(__file__), "static")
if os.path.isdir(_static):
    app.mount("/static", StaticFiles(directory=_static), name="static")

@app.get("/")
def root():
    index = os.path.join(_static, "index.html")
    if os.path.exists(index):
        return FileResponse(index)
    return {"status": "ok", "app": settings.app_name}

@app.get("/health")
def health():
    return {"status": "healthy"}