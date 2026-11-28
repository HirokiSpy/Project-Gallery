import getpass
import json
import os
import secrets
from pathlib import Path

from werkzeug.security import generate_password_hash

BASE_DIR = Path(__file__).resolve().parent
CONFIG_DIR = BASE_DIR / "instance"
CONFIG_FILE = CONFIG_DIR / "admin_config.json"


def _prompt_password(prompt_text: str, confirm_text: str, min_len: int) -> str:
    while True:
        password = getpass.getpass(prompt_text)
        if len(password) < min_len:
            print(f"Password must be at least {min_len} characters long.")
            continue
        confirmation = getpass.getpass(confirm_text)
        if password != confirmation:
            print("Passwords do not match. Try again.")
            continue
        return password


def configure_admin_password():
    """Set gallery passcode and admin password, saving only their hashes locally."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    try:
        config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        config = {}

    # 1. Gallery Access Passcode (for visitors/members)
    if config.get("gallery_passcode_hash"):
        change_gallery = input("Gallery access passcode already exists. Change it? (y/N): ").strip().lower()
        if change_gallery == "y":
            passcode = _prompt_password(
                "Set new gallery access passcode (min 4 characters): ",
                "Confirm gallery access passcode: ",
                4,
            )
            config["gallery_passcode_hash"] = generate_password_hash(passcode)
    else:
        passcode = _prompt_password(
            "Set gallery access passcode (min 4 characters): ",
            "Confirm gallery access passcode: ",
            4,
        )
        config["gallery_passcode_hash"] = generate_password_hash(passcode)

    # 2. Admin Password (for owner privileges)
    if config.get("admin_password_hash") and config.get("secret_key"):
        change_admin = input("Admin password already exists. Change it? (y/N): ").strip().lower()
        if change_admin == "y":
            admin_pw = _prompt_password(
                "Set new admin password (min 8 characters): ",
                "Confirm admin password: ",
                8,
            )
            config["admin_password_hash"] = generate_password_hash(admin_pw)
    else:
        admin_pw = _prompt_password(
            "Set new admin password (min 8 characters): ",
            "Confirm admin password: ",
            8,
        )
        config["admin_password_hash"] = generate_password_hash(admin_pw)

    config.setdefault("secret_key", secrets.token_hex(32))
    CONFIG_FILE.write_text(json.dumps(config, indent=2), encoding="utf-8")
    try:
        os.chmod(CONFIG_FILE, 0o600)
    except OSError:
        pass
    print(f"Configuration saved locally in {CONFIG_FILE.name}; do not share this file.")
    return config


def load_config():
    try:
        config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError("Configuration missing or corrupted. Run run_galeri.py to set up.") from exc
    if not config.get("admin_password_hash") or not config.get("gallery_passcode_hash") or not config.get("secret_key"):
        raise RuntimeError("Configuration incomplete. Run run_galeri.py to set up.")
    return config
