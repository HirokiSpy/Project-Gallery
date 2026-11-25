import hmac
import json
import os
import time
import uuid
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, session
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from security_config import configure_admin_password, load_config

BASE_DIR = Path(__file__).resolve().parent
if __name__ == "__main__" and os.environ.get("GALLERY_CONFIG_READY") != "1":
    configure_admin_password()
CONFIG = load_config()

app = Flask(__name__)
app.secret_key = CONFIG["secret_key"]
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    MAX_CONTENT_LENGTH=10 * 1024 * 1024,
)

admin_online = False
FOLDER_GAMBAR = BASE_DIR / "uploads"
FAIL_DATA = BASE_DIR / "data.json"
EXTENSIONS_GAMBAR = {"png", "jpg", "jpeg", "gif", "webp"}
FOLDER_GAMBAR.mkdir(exist_ok=True)
if not FAIL_DATA.exists():
    FAIL_DATA.write_text("[]", encoding="utf-8")


def baca_data():
    try:
        with FAIL_DATA.open("r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, list) else []
    except (OSError, json.JSONDecodeError):
        app.logger.exception("Gagal membaca data galeri")
        return []


def simpan_data(data):
    sementara = FAIL_DATA.with_suffix(".tmp")
    with sementara.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)
    sementara.replace(FAIL_DATA)


def sahkan_pin(pin_diberi, item):
    pin_hash = item.get("pin_hash", "")
    if pin_hash:
        try:
            return check_password_hash(pin_hash, pin_diberi), pin_hash
        except (ValueError, TypeError):
            return False, pin_hash

    # Sokong rekod lama buat sementara dan hashkan PIN selepas pengesahan berjaya.
    pin_lama = item.get("pin", "")
    if pin_lama and hmac.compare_digest(pin_diberi, pin_lama):
        return True, generate_password_hash(pin_lama)
    return False, pin_hash


@app.route("/", methods=["GET", "POST"])
def utama():
    if request.method == "POST":
        nama_pengirim = (request.form.get("nama") or "Tanpa Nama").strip()[:40]
        pin_padam = (request.form.get("pin") or "").strip()
        warna_nama = (request.form.get("warna_nama") or "#c084fc").strip()
        fail = request.files.get("gambar")
        if fail and fail.filename:
            nama_asal = secure_filename(fail.filename)
            if "." not in nama_asal or nama_asal.rsplit(".", 1)[1].lower() not in EXTENSIONS_GAMBAR:
                return "Jenis fail gambar tidak disokong.", 400
            sambungan = nama_asal.rsplit(".", 1)[1].lower()
            nama_selamat = f"{uuid.uuid4().hex}.{sambungan}"
            fail.save(FOLDER_GAMBAR / nama_selamat)
            rekod = baca_data()
            rekod.insert(0, {
                "nama": nama_pengirim,
                "fail": nama_selamat,
                "ada_pin": bool(pin_padam),
                "pin_hash": generate_password_hash(pin_padam) if pin_padam else "",
                "warna": warna_nama,
            })
            simpan_data(rekod)
        return redirect("/")

    senarai_data = baca_data()
    return render_template(
        "index.html",
        senarai_data=senarai_data,
        is_admin=bool(session.get("is_admin")),
        admin_online=admin_online,
    )


@app.route("/admin/login", methods=["POST"])
def admin_login():
    global admin_online
    data = request.get_json(silent=True) or {}
    katalaluan = (data.get("password") or request.form.get("password") or "").strip()
    if check_password_hash(CONFIG["admin_password_hash"], katalaluan):
        session.clear()
        session["is_admin"] = True
        admin_online = True
        return jsonify({"ok": True, "is_admin": True, "admin_online": True})
    return jsonify({"ok": False, "error": "Kata laluan admin salah."}), 401


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    global admin_online
    session.clear()
    admin_online = False
    return jsonify({"ok": True, "is_admin": False, "admin_online": False})


@app.route("/admin/status")
def admin_status():
    return jsonify({"admin_online": admin_online})


@app.route("/uploads/<nama_fail>")
def papar_gambar(nama_fail):
    return send_from_directory(FOLDER_GAMBAR, os.path.basename(nama_fail))


@app.route("/delete", methods=["POST"])
def padam_gambar():
    data = request.get_json(silent=True) or {}
    nama_fail = os.path.basename(data.get("fail", ""))
    pin_diberi = (data.get("pin") or "").strip()
    is_admin = bool(session.get("is_admin"))
    if not nama_fail:
        return jsonify({"ok": False, "error": "Nama fail tiada."}), 400

    rekod = baca_data()
    item_padam = next((item for item in rekod if item.get("fail") == nama_fail), None)
    if not item_padam:
        return jsonify({"ok": False, "error": "Rekod gambar tidak dijumpai."}), 404

    if not is_admin:
        if not (item_padam.get("pin_hash") or item_padam.get("pin")):
            return jsonify({"ok": False, "error": "Gambar ini tiada PIN dan tidak boleh dipadam."}), 403
        sah, hash_baru = sahkan_pin(pin_diberi, item_padam)
        if not sah:
            return jsonify({"ok": False, "error": "PIN salah! Gambar tidak dipadam."}), 403
        if hash_baru and not item_padam.get("pin_hash"):
            item_padam["pin_hash"] = hash_baru
            item_padam.pop("pin", None)
            simpan_data(rekod)

    laluan_fail = FOLDER_GAMBAR / nama_fail
    if laluan_fail.exists():
        laluan_fail.unlink()
    simpan_data([item for item in rekod if item.get("fail") != nama_fail])
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
