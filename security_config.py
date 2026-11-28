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


def _prompt_gallery_pin() -> str:
    while True:
        pin = getpass.getpass(
            "Set gallery PIN (exactly 4 digits): "
        ).strip()

        if len(pin) != 4 or not pin.isdigit():
            print("Gallery PIN must be exactly 4 digits.")
            continue

        confirmation = getpass.getpass("Confirm gallery PIN: ").strip()
        if pin != confirmation:
            print("PINs do not match. Try again.")
            continue

        return pin


def configure_admin_password():
    """Configure the shared gallery PIN and legacy admin password."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)

    try:
        config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        config = {}

    if config.get("gallery_passcode_hash"):
        change_gallery = input(
            "Gallery PIN already exists. Change it? (y/N): "
        ).strip().lower()

        if change_gallery == "y":
            config["gallery_passcode_hash"] = generate_password_hash(
                _prompt_gallery_pin()
            )
    else:
        config["gallery_passcode_hash"] = generate_password_hash(
            _prompt_gallery_pin()
        )

    if config.get("admin_password_hash") and config.get("secret_key"):
        change_admin = input(
            "Legacy admin password already exists. Change it? (y/N): "
        ).strip().lower()

        if change_admin == "y":
            admin_password = _prompt_password(
                "Set admin password (min 8 characters): ",
                "Confirm admin password: ",
                8,
            )
            config["admin_password_hash"] = generate_password_hash(
                admin_password
            )
    else:
        admin_password = _prompt_password(
            "Set admin password (min 8 characters): ",
            "Confirm admin password: ",
            8,
        )
        config["admin_password_hash"] = generate_password_hash(
            admin_password
        )

    config.setdefault("secret_key", secrets.token_hex(32))
    CONFIG_FILE.write_text(
        json.dumps(config, indent=2),
        encoding="utf-8",
    )

    try:
        os.chmod(CONFIG_FILE, 0o600)
    except OSError:
        pass

    print(
        f"Configuration saved locally in {CONFIG_FILE.name}; "
        "do not share this file."
    )
    return config


def load_config():
    try:
        config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise RuntimeError(
            "Configuration missing or corrupted. "
            "Run the setup script first."
        ) from exc

    if (
        not config.get("admin_password_hash")
        or not config.get("gallery_passcode_hash")
        or not config.get("secret_key")
    ):
        raise RuntimeError(
            "Configuration incomplete. Run the setup script first."
        )

    return config
