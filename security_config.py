import getpass
import json
import os
import secrets
from pathlib import Path

from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "instance"
CONFIG_FILE = CONFIG_DIR / "admin_config.json"


def configure_admin_password():
    """Ask for a new admin password and save only its hash locally."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        config = {}

    while True:
        password = getpass.getpass("Set kata laluan admin (minimum 12 aksara): ")
        if len(password) < 12:
            print("Kata laluan mesti sekurang-kurangnya 12 aksara.")
            continue
        confirmation = getpass.getpass("Masukkan semula kata laluan admin: ")
        if password != confirmation:
            print("Kata laluan tidak sepadan. Cuba lagi.")
            continue
        break

    config["admin_password_hash"] = generate_password_hash(password)
    config.setdefault("secret_key", secrets.token_hex(32))
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except OSError:
        pass
    print(f"Tetapan disimpan secara lokal dalam {CONFIG_FILE.name}; jangan kongsi fail ini.")
    return config


def load_config():
    try:
        config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("Konfigurasi admin tiada atau rosak. Jalankan run_galeri.py untuk setup.") from exc
    if not config.get("admin_password_hash") or not config.get("secret_key"):
        raise RuntimeError("Konfigurasi admin tidak lengkap. Jalankan run_galeri.py untuk setup.")
    return config
