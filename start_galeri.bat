@echo off
title Galeri Gambar - Flask + Cloudflare
cd /d "%~dp0"
python run_galeri.py
if errorlevel 1 (
    echo.
    echo [RALAT] Galeri gagal dimulakan. Pastikan Python dan cloudflared tersedia.
    pause
)
