@echo off
title Galeri Gambar - Flask + Cloudflare
cd /d "%~dp0"
python start_website.py
if errorlevel 1 (
    echo.
    echo [RALAT] Galeri gagal dimulakan. Pastikan Python dan cloudflared tersedia.
    pause
)
