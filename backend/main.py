# backend/main.py
# -*- coding: utf-8 -*-
"""FastAPI backend for AI Novel Editor"""

import sys
import os
import argparse
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from api import novels, characters, world_bible, outline, chapters, settings, generate, foreshadowing, chapter_generate, scenes, prompts_editor

app = FastAPI(title="AI Novel Editor Backend", version="0.1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ─────────────────────────────────────────────────────

app.include_router(novels.router, prefix="/api")
app.include_router(characters.router, prefix="/api")
app.include_router(world_bible.router, prefix="/api")
app.include_router(outline.router, prefix="/api")
app.include_router(chapters.router, prefix="/api")
app.include_router(settings.router, prefix="/api")
app.include_router(generate.router, prefix="/api")
app.include_router(foreshadowing.router, prefix="/api")
app.include_router(chapter_generate.router, prefix="/api")
app.include_router(scenes.router, prefix="/api")
app.include_router(prompts_editor.router, prefix="/api")


@app.get("/api/health")
def health():
    return {"status": "ok"}


# ─── Serve Frontend (when built) ──────────────────────────────────

FRONTEND_DIST = os.path.join(os.path.dirname(os.path.dirname(__file__)), "dist")

if os.path.isdir(FRONTEND_DIST):
    app.mount("/assets", StaticFiles(directory=os.path.join(FRONTEND_DIST, "assets")), name="assets")

    @app.get("/{path:path}")
    async def serve_frontend(path: str):
        file_path = os.path.join(FRONTEND_DIST, path)
        if os.path.isfile(file_path):
            return FileResponse(file_path)
        return FileResponse(os.path.join(FRONTEND_DIST, "index.html"))



if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8765)
    args = parser.parse_args()

    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=args.port, log_level="info")
