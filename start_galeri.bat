@echo off
title Galeri Gambar - Flask + Cloudflare
cd /d "%~dp0"
setlocal

echo Masukkan kata laluan admin untuk sesi ini.
set /p "ADMIN_PASSWORD=ADMIN_PASSWORD: "
if not defined ADMIN_PASSWORD (
    echo [RALAT] Kata laluan admin tidak boleh kosong.
    pause
    exit /b 1
)

for /f %%A in ('python -c "import secrets; print(secrets.token_hex(32))"') do set "SECRET_KEY=%%A"
if not defined SECRET_KEY (
    echo [RALAT] Gagal menjana SECRET_KEY. Pastikan Python tersedia.
    pause
    exit /b 1
)
where cloudflared >nul 2>nul
if errorlevel 1 (
    echo [RALAT] cloudflared tidak dijumpai dalam PATH.
    pause
    exit /b 1
)

echo [1/2] Memulakan pelayan Flask...
start "Flask Galeri" python app.py
timeout /t 2 /nobreak >nul

echo [2/2] Memulakan Cloudflare Tunnel...
cloudflared tunnel --url http://127.0.0.1:5000

echo.
echo Tunnel ditutup. Menutup proses Flask...
taskkill /FI "WINDOWTITLE eq Flask Galeri*" /F >nul 2>nul
pause
