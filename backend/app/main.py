from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.api.assets import router as assets_router
from app.api.auth import router as auth_router
from app.api.clips import router as clips_router
from app.api.jobs import router as jobs_router
from app.api.music import router as music_router
from app.api.projects import router as projects_router
from app.api.render import router as render_router
from app.api.themes import router as themes_router
from app.api.tiny import router as tiny_router
from app.core.config import get_settings
from app.core.logging import configure_logging

configure_logging("backend.log")

app = FastAPI(title="Ambient Video AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth_router)
app.include_router(themes_router)
app.include_router(projects_router)
app.include_router(clips_router)
app.include_router(jobs_router)
app.include_router(assets_router)
app.include_router(music_router)
app.include_router(render_router)
app.include_router(tiny_router)
media_root = Path(get_settings().media_root)
media_root.mkdir(parents=True, exist_ok=True)
app.mount("/media", StaticFiles(directory=media_root), name="media")


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}
