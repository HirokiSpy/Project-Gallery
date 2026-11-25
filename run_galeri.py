import os
import shutil
import subprocess
import sys
import time

PORT = int(os.environ.get("PORT", 5000))
TARGET_URL = f"http://127.0.0.1:{PORT}"


def cari_cloudflared() -> str | None:
    # Semak dalam PATH sistem dahulu
    di_path = shutil.which("cloudflared")
    if di_path:
        return di_path

    # Semak lokasi biasa pada Windows
    calon_windows = [
        r"C:\Program Files (x86)\cloudflared\cloudflared.exe",
        r"C:\Program Files\cloudflared\cloudflared.exe",
    ]
    for laluan in calon_windows:
        if os.path.exists(laluan):
            return laluan

    return None


def utama():
    cf_bin = cari_cloudflared()
    if not cf_bin:
        print("[RALAT] 'cloudflared' tidak dijumpai. Sila pasang Cloudflare Tunnel dahulu.")
        sys.exit(1)

    print(f"[1/2] Menjalankan Flask ({TARGET_URL})...")
    proses_flask = subprocess.Popen(
        [sys.executable, "app.py"],
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )

    # Beri masa seketika supaya Flask bersedia menerima sambungan
    time.sleep(2)

    print("[2/2] Memulakan Cloudflare Tunnel...")
    proses_cf = subprocess.Popen(
        [cf_bin, "tunnel", "--url", TARGET_URL],
        cwd=os.path.dirname(os.path.abspath(__file__)),
    )

    print("\n--- Galeri Gambar sedang berjalan! Tekan Ctrl + C untuk hentikan semua. ---\n")

    try:
        while True:
            if proses_flask.poll() is not None:
                print("[INFO] Proses Flask telah berhenti.")
                break
            if proses_cf.poll() is not None:
                print("[INFO] Proses Cloudflare Tunnel telah berhenti.")
                break
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[STOP] Menghentikan Cloudflare Tunnel dan Flask...")
    finally:
        for p in (proses_cf, proses_flask):
            if p.poll() is None:
                p.terminate()
                try:
                    p.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    p.kill()
        print("[SELESAI] Semua proses ditutup.")


if __name__ == "__main__":
    utama()