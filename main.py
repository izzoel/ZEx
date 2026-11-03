
#!/usr/bin/env python3
"""
ZEX — ZTV Extractor API
FastAPI entry point untuk extractor.py.

Endpoint:
    GET /
    GET /health
    GET /extract

Jalankan:
    python -m uvicorn main:app --host 0.0.0.0 --port 8000
"""

import os
import logging
from typing import Any
from urllib.parse import urlparse

from fastapi import FastAPI, Query, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse

from extractor import main as extract_main

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("zex")

app = FastAPI(
    title="ZEX — ZTV Extractor API",
    description="API untuk mendeteksi stream HLS dan menjalankan extractor ZEX.",
    version="1.0.0",
)

# Definisi Path Folder Storage Movies
MOVIES_DIR = "/home/user/ZEx/storage/movies"

# CORS
cors_origins_env = os.getenv("CORS_ORIGINS", "*").strip()

cors_origins = (
    ["*"]
    if cors_origins_env == "*"
    else [
        origin.strip()
        for origin in cors_origins_env.split(",")
        if origin.strip()
    ]
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=False,
    allow_methods=["GET", "OPTIONS"],
    allow_headers=["*"],
)


@app.get("/", tags=["Status"])
def root() -> dict[str, str]:
    return {
        "name": "ZEX — ZTV Extractor API",
        "status": "online",
        "docs": "/docs",
        "endpoint": "/extract",
        "endpoint_movies": "/movies/{filename}",
    }


@app.get("/health", tags=["Status"])
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.get("/extract", tags=["Extraction"])
def extract(
    m3u8_url: str = Query(
        ...,
        min_length=1,
        description="URL halaman tontonan Cinema Zetware",
    )
) -> dict[str, Any]:

    parsed = urlparse(m3u8_url.strip())

    if (
        parsed.scheme != "https"
        or parsed.hostname != "cinema.zetware.id"
        or not parsed.path.startswith("/watch/")
    ):
        return {
            "status": "failed",
            "error_reason": "URL halaman tontonan tidak valid.",
        }

    try:
        logger.info("Memulai ekstraksi: %s", parsed.path)

        # extractor.py saat ini belum mendukung enable_download.
        extract_main(m3u8_url.strip())

        return {
            "status": "completed",
            "message": "Proses extractor selesai. Periksa log server untuk hasil ekstraksi.",
            "metadata": {
                "url": m3u8_url.strip(),
            },
        }

    except Exception:
        logger.exception("Terjadi kesalahan saat menjalankan extractor")

        return {
            "status": "failed",
            "error_reason": (
                "Terjadi kesalahan internal saat menjalankan ekstraksi. "
                "Periksa log server."
            ),
        }

@app.get("/movies/{filename}", tags=["Storage"])
def download_movie(filename: str) -> FileResponse:
    """Endpoint untuk mendownload file MP4 dari storage/movies."""
    # Menghindari Path Traversal Attack dengan os.path.basename
    safe_filename = os.path.basename(filename)
    file_path = os.path.join(MOVIES_DIR, safe_filename)

    if not os.path.isfile(file_path):
        raise HTTPException(status_code=404, detail="File video tidak ditemukan.")

    return FileResponse(
        path=file_path,
        filename=safe_filename,
        media_type="video/mp4"
    )

if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )
