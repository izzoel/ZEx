#!/usr/bin/env python3
"""
ZEX — ZTV Extractor API
FastAPI entry point untuk extractor.py.

Endpoint:
    GET /extract
    GET /health
    GET /

Jalankan:
    uvicorn main:app --host 0.0.0.0 --port 8000
"""

import os
from typing import Any

from fastapi import FastAPI, Query
from fastapi.middleware.cors import CORSMiddleware

from extractor import DetailedM3U8Monitor


app = FastAPI(
    title="ZEX — ZTV Extractor API",
    description="API untuk mendeteksi stream HLS dan opsional mengunduh resolusi yang tersedia.",
    version="1.0.0",
)

# Atur CORS_ORIGINS dengan daftar origin dipisahkan koma bila ingin membatasi akses.
# Contoh: CORS_ORIGINS="https://cinema.zetware.id,http://localhost:3000"
cors_origins_env = os.getenv("CORS_ORIGINS", "*").strip()
cors_origins = (
    ["*"]
    if cors_origins_env == "*"
    else [origin.strip() for origin in cors_origins_env.split(",") if origin.strip()]
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
    """Informasi singkat API."""
    return {
        "name": "ZEX — ZTV Extractor API",
        "status": "online",
        "docs": "/docs",
        "endpoint": "/extract",
    }


@app.get("/health", tags=["Status"])
def health() -> dict[str, str]:
    """Health check sederhana tanpa menjalankan ekstraksi."""
    return {"status": "ok"}


@app.get("/extract", tags=["Extraction"])
def extract(
    tmdb_id: str = Query(..., min_length=1, description="ID TMDB tanpa prefix, misalnya 456"),
    m3u8_url: str = Query(
        ...,
        description="URL halaman tontonan atau URL master.m3u8 yang dapat diakses",
    ),
    title: str = Query(..., min_length=1, description="Judul film atau serial"),
    enable_download: bool = Query(
        True,
        description="Aktifkan pengunduhan dan proses upload yang ditangani extractor.py",
    ),
    test_download: bool = Query(
        False,
        description="Mode uji sesuai implementasi extractor.py",
    ),
    threads: int = Query(
        8,
        ge=1,
        le=32,
        description="Jumlah concurrent fragment download; antara 1 dan 32",
    ),
) -> dict[str, Any]:
    """Jalankan extractor.py dengan parameter query yang dipakai frontend."""
    try:
        monitor = DetailedM3U8Monitor(headless=True)
        result = monitor.extract_stream(
            tmdb_id=tmdb_id.strip(),
            target_url=m3u8_url.strip(),
            title=title.strip(),
            enable_download=enable_download,
            test_download=test_download,
            threads=threads,
        )

        if isinstance(result, dict):
            return result

        return {
            "status": "failed",
            "error_reason": "Extractor mengembalikan hasil dengan format yang tidak dikenal.",
        }

    except Exception:
        # Jangan kirim exception mentah ke client karena dapat memuat URL stream bertoken.
        return {
            "status": "failed",
            "error_reason": (
                "Terjadi kesalahan internal saat menjalankan ekstraksi. "
                "Periksa log server untuk detailnya."
            ),
            "metadata": {"title": title, "tmdb_id": tmdb_id},
        }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
        reload=False,
    )
