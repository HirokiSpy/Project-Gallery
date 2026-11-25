import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

from security_config import configure_admin_password

PORT = int(os.environ.get("PORT", 5000))
TARGET_URL = f"http://127.0.0.1:{PORT}"


def cari_cloudflared() -> str | None:
    di_path = shutil.which("cloudflared")
    if di_path:
        return di_path
    for laluan in (
        r"C:\Program Files (x86)\cloudflared\cloudflared.exe",
        r"C:\Program Files\cloudflared\cloudflared.exe",
    ):
        if os.path.exists(laluan):
            return laluan
    return None


def utama():
    # Tanya dan simpan hash admin setiap kali launcher dijalankan.
    configure_admin_password()
    cf_bin = cari_cloudflared()
    if not cf_bin:
        print("[RALAT] 'cloudflared' tidak dijumpai. Sila pasang Cloudflare Tunnel dahulu.")
        sys.exit(1)

    env = os.environ.copy()
    env["GALLERY_CONFIG_READY"] = "1"
    print(f"[1/2] Menjalankan Flask ({TARGET_URL})...")
    proses_flask = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=Path(__file__).resolve().parent,
        env=env,
    )
    time.sleep(2)
    if proses_flask.poll() is not None:
        print("[RALAT] Pelayan Flask gagal dimulakan.")
        sys.exit(proses_flask.returncode or 1)

    print("[2/2] Memulakan Cloudflare Tunnel...")
    proses_cf = subprocess.Popen(
        [cf_bin, "tunnel", "--url", TARGET_URL],
        cwd=Path(__file__).resolve().parent,
    )
    print("\n--- Galeri Gambar sedang berjalan! Tekan Ctrl + C untuk hentikan semua. ---\n")
    try:
        while True:
            if proses_flask.poll() is not None or proses_cf.poll() is not None:
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[STOP] Menghentikan Cloudflare Tunnel dan Flask...")
    finally:
        for proses in (proses_cf, proses_flask):
            if proses.poll() is None:
                proses.terminate()
                try:
                    proses.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    proses.kill()
        print("[SELESAI] Semua proses ditutup.")


if __name__ == "__main__":
    utama()
