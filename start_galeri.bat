@echo off
title Galeri Gambar - Flask + Cloudflare
cd /d "%~dp0"

echo [1/2] Memulakan pelayan Flask...
start "Flask Galeri" python app.py

timeout /t 2 /nobreak >nul

echo [2/2] Memulakan Cloudflare Tunnel...
cloudflared tunnel --url http://127.0.0.1:5000

echo.
echo Tunnel ditutup. Menutup proses Flask...
taskkill /FI "WINDOWTITLE eq Flask Galeri*" /F >nul 2>nul
pause