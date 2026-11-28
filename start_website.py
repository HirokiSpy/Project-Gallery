import os
import re
import shutil
import subprocess
import sys
import threading
import time
from pathlib import Path

from security_config import configure_admin_password

BASE_DIR = Path(__file__).resolve().parent
PORT = int(os.environ.get("PORT", 5000))
TARGET_URL = f"http://127.0.0.1:{PORT}"
URL_FILE = BASE_DIR / "instance" / "tunnel_url.txt"
ENV_FILE = BASE_DIR / ".env"


def load_local_env():
    if not ENV_FILE.exists():
        return
    try:
        for line in ENV_FILE.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            key, value = line.split("=", 1)
            os.environ.setdefault(
                key.strip(),
                value.strip().strip('"').strip("'"),
            )
    except OSError:
        pass


def find_cloudflared():
    in_path = shutil.which("cloudflared")
    if in_path:
        return in_path

    for path in (
        r"C:\Program Files (x86)\cloudflared\cloudflared.exe",
        r"C:\Program Files\cloudflared\cloudflared.exe",
    ):
        if os.path.exists(path):
            return path
    return None


def monitor_quick_tunnel_url(cf_process):
    pattern = re.compile(
        r"https://[a-zA-Z0-9-]+\.trycloudflare\.com"
    )
    if cf_process.stderr:
        for line in iter(cf_process.stderr.readline, ""):
            match = pattern.search(line)
            if match:
                URL_FILE.parent.mkdir(parents=True, exist_ok=True)
                URL_FILE.write_text(match.group(0), encoding="utf-8")


def choose_tunnel_mode():
    print("\n========================================================")
    print("  SELECT SERVER CONNECTION MODE")
    print("========================================================")
    print("  1. Cloudflare Quick Tunnel (Free - No Domain Required)")
    print("  2. Cloudflare Zero Trust   (Custom Domain)")
    print("  3. Local Only              (Wi-Fi / Localhost)")
    print("========================================================")

    while True:
        choice = input(
            "Enter your choice (1 / 2 / 3) [Default: 1]: "
        ).strip() or "1"
        if choice in {"1", "2", "3"}:
            return choice
        print("Invalid choice. Please enter 1, 2, or 3.")


def main():
    load_local_env()
    configure_admin_password()

    if URL_FILE.exists():
        URL_FILE.unlink()
    URL_FILE.parent.mkdir(parents=True, exist_ok=True)

    mode = choose_tunnel_mode()
    cf_process = None

    if mode == "1":
        cf_bin = find_cloudflared()
        if not cf_bin:
            print("\n[ERROR] 'cloudflared' was not found.")
            input("Press Enter to exit...")
            sys.exit(1)

        cf_process = subprocess.Popen(
            [cf_bin, "tunnel", "--url", TARGET_URL],
            cwd=BASE_DIR,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.PIPE,
            text=True,
            encoding="utf-8",
            errors="replace",
        )

        threading.Thread(
            target=monitor_quick_tunnel_url,
            args=(cf_process,),
            daemon=True,
        ).start()

        for _ in range(30):
            if URL_FILE.exists() or cf_process.poll() is not None:
                break
            time.sleep(0.5)

    elif mode == "2":
        domain = (
            os.environ.get("CF_DOMAIN")
            or input("Enter your Zero Trust domain: ").strip()
        )
        if not domain.startswith("http"):
            domain = f"https://{domain}"

        URL_FILE.write_text(domain, encoding="utf-8")

        token = os.environ.get("CF_TUNNEL_TOKEN", "").strip()
        if token:
            cf_bin = find_cloudflared()
            if cf_bin:
                cf_process = subprocess.Popen(
                    [cf_bin, "tunnel", "run", "--token", token],
                    cwd=BASE_DIR,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )

    else:
        URL_FILE.write_text(TARGET_URL, encoding="utf-8")

    os.environ["GALLERY_CONFIG_READY"] = "1"

    from app import app

    print(f"\nServer is starting at http://127.0.0.1:{PORT}")
    print("Press CTRL+C to stop.\n")

    try:
        app.run(
            host="0.0.0.0",
            port=PORT,
            debug=False,
            use_reloader=False,
        )
    except KeyboardInterrupt:
        pass
    finally:
        if cf_process and cf_process.poll() is None:
            cf_process.terminate()
            try:
                cf_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                cf_process.kill()

        if URL_FILE.exists():
            URL_FILE.unlink()

        print("\n[DONE] Server stopped.")


if __name__ == "__main__":
    try:
        main()
    except Exception as error:
        print(f"\n[CRITICAL ERROR] {error}")
        input("Press Enter to close this window...")
