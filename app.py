import ipaddress
import json
import logging
import os
import re
import threading
import uuid
from pathlib import Path

from flask import (
    Flask,
    jsonify,
    redirect,
    render_template,
    request,
    send_from_directory,
    session,
)
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from security_config import load_config

BASE_DIR = Path(__file__).resolve().parent
CONFIG = load_config()

logging.getLogger("werkzeug").setLevel(logging.ERROR)

app = Flask(__name__)
app.secret_key = CONFIG["secret_key"]
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("GALLERY_HTTPS", "0") == "1",
    MAX_CONTENT_LENGTH=10 * 1024 * 1024,
)

FOLDER_GAMBAR = BASE_DIR / "uploads"
FAIL_DATA = BASE_DIR / "data.json"
FAIL_AKAUN = BASE_DIR / "instance" / "users.json"

EXTENSIONS_GAMBAR = {"png", "jpg", "jpeg", "gif", "webp"}
NAMA_AKAUN = re.compile(r"^[A-Za-z0-9_.-]{3,32}$")
PIN_4_DIGIT = re.compile(r"^\d{4}$")

KUNCI_DATA = threading.RLock()
KUNCI_AKAUN = threading.RLock()
KUNCI_RATE = threading.Lock()

HAD_CUBAAN = 5
TEMPOH_SEKAT = 120
CUBAAAN_GAGAL = {}

FOLDER_GAMBAR.mkdir(exist_ok=True)
FAIL_AKAUN.parent.mkdir(parents=True, exist_ok=True)

if not FAIL_DATA.exists():
    FAIL_DATA.write_text("[]", encoding="utf-8")

if not FAIL_AKAUN.exists():
    FAIL_AKAUN.write_text("{}", encoding="utf-8")


def _kunci_login():
    return request.remote_addr or "unknown"


def _baki_sekat():
    import time

    with KUNCI_RATE:
        rekod = CUBAAAN_GAGAL.get(_kunci_login(), {})
    return max(0, int(rekod.get("tamat", 0) - time.time()))


def _gagal_login():
    import time

    with KUNCI_RATE:
        kunci = _kunci_login()
        rekod = CUBAAAN_GAGAL.setdefault(
            kunci,
            {"bil": 0, "tamat": 0},
        )
        rekod["bil"] += 1

        if rekod["bil"] >= HAD_CUBAAN:
            rekod["tamat"] = time.time() + TEMPOH_SEKAT
            rekod["bil"] = 0


def _reset_login():
    with KUNCI_RATE:
        CUBAAAN_GAGAL.pop(_kunci_login(), None)


def baca_data():
    with KUNCI_DATA:
        try:
            data = json.loads(FAIL_DATA.read_text(encoding="utf-8"))
            if not isinstance(data, list):
                return []

            for item in data:
                if not isinstance(item.get("likes"), int):
                    item["likes"] = int(item.get("likes") or 0)
                if not isinstance(item.get("comments"), list):
                    item["comments"] = []

            return data
        except (OSError, json.JSONDecodeError):
            return []


def simpan_data(data):
    with KUNCI_DATA:
        sementara = FAIL_DATA.with_suffix(".tmp")

        with sementara.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False, indent=2)
            file.flush()
            os.fsync(file.fileno())

        sementara.replace(FAIL_DATA)


def baca_akaun():
    try:
        data = json.loads(FAIL_AKAUN.read_text(encoding="utf-8"))
        return data if isinstance(data, dict) else {}
    except (OSError, json.JSONDecodeError):
        return {}


def ada_akses_galeri():
    return bool(session.get("username"))


@app.before_request
def kawalan_pintu_masuk():
    laluan_bebas = {"utama", "auth", "static"}
    if request.endpoint in laluan_bebas:
        return None

    if request.path.startswith("/uploads/") and not ada_akses_galeri():
        return "Sila log masuk untuk melihat gambar.", 403

    if not ada_akses_galeri():
        return jsonify({
            "ok": False,
            "error": "Sila log masuk dan masukkan PIN galeri dahulu.",
        }), 403

    return None


@app.route("/", methods=["GET", "POST"])
def utama():
    if not ada_akses_galeri():
        return render_template("index.html", logged_in=False)

    if request.method == "POST":
        description = (
            request.form.get("description") or ""
        ).strip()[:160]
        show_username = request.form.get("show_username") == "yes"
        upload = request.files.get("gambar")

        if not upload or not upload.filename:
            return "Sila pilih gambar untuk dimuat naik.", 400

        nama_asal = secure_filename(upload.filename)
        extension = Path(nama_asal).suffix.lstrip(".").lower()

        if extension not in EXTENSIONS_GAMBAR:
            return "Jenis fail gambar tidak disokong.", 400

        if not (upload.mimetype or "").startswith("image/"):
            return "Kandungan fail bukan imej.", 400

        filename = f"{uuid.uuid4().hex}.{extension}"
        filepath = FOLDER_GAMBAR / filename
        upload.save(filepath)

        records = baca_data()
        records.insert(0, {
            "fail": filename,
            "description": description,
            "username": session["username"],
            "show_username": show_username,
            "likes": 0,
            "comments": [],
        })

        try:
            simpan_data(records)
        except OSError:
            filepath.unlink(missing_ok=True)
            return "Gagal menyimpan rekod gambar.", 500

        return redirect("/")

    return render_template(
        "index.html",
        logged_in=True,
        username=session["username"],
        images=baca_data(),
    )


@app.route("/auth", methods=["POST"])
def auth():
    baki = _baki_sekat()
    if baki:
        return jsonify({
            "ok": False,
            "error": f"Terlalu banyak cubaan. Cuba lagi dalam {baki} saat.",
        }), 429

    payload = request.get_json(silent=True) or request.form
    username = (payload.get("username") or "").strip()
    password = payload.get("password") or ""
    pin = (payload.get("pin") or "").strip()

    if not NAMA_AKAUN.fullmatch(username):
        _gagal_login()
        return jsonify({
            "ok": False,
            "error": (
                "Username mesti 3–32 aksara "
                "(huruf, nombor, titik, _ atau -)."
            ),
        }), 400

    if len(password) < 8:
        _gagal_login()
        return jsonify({
            "ok": False,
            "error": "Password mesti sekurang-kurangnya 8 aksara.",
        }), 400

    if not PIN_4_DIGIT.fullmatch(pin):
        _gagal_login()
        return jsonify({
            "ok": False,
            "error": "PIN galeri mesti tepat 4 digit.",
        }), 400

    try:
        pin_sah = check_password_hash(
            CONFIG["gallery_passcode_hash"],
            pin,
        )
    except (ValueError, TypeError):
        pin_sah = False

    if not pin_sah:
        _gagal_login()
        return jsonify({
            "ok": False,
            "error": "PIN galeri salah.",
        }), 401

    account_key = username.casefold()

    with KUNCI_AKAUN:
        accounts = baca_akaun()
        account = accounts.get(account_key)

        if account:
            try:
                password_sah = check_password_hash(
                    account.get("password_hash", ""),
                    password,
                )
            except (ValueError, TypeError):
                password_sah = False

            if not password_sah:
                _gagal_login()
                return jsonify({
                    "ok": False,
                    "error": "Password salah untuk username ini.",
                }), 401
        else:
            accounts[account_key] = {
                "username": username,
                "password_hash": generate_password_hash(password),
            }

            sementara = FAIL_AKAUN.with_suffix(".tmp")
            sementara.write_text(
                json.dumps(accounts, ensure_ascii=False, indent=2),
                encoding="utf-8",
            )
            sementara.replace(FAIL_AKAUN)

            try:
                os.chmod(FAIL_AKAUN, 0o600)
            except OSError:
                pass

    _reset_login()
    session.clear()
    session["username"] = accounts[account_key]["username"]

    return jsonify({
        "ok": True,
        "created": account is None,
    })


@app.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"ok": True})


@app.route("/like/<nama_fail>", methods=["POST"])
def like_gambar(nama_fail):
    filename = os.path.basename(nama_fail)

    with KUNCI_DATA:
        records = baca_data()
        image = next(
            (item for item in records if item.get("fail") == filename),
            None,
        )

        if not image:
            return jsonify({
                "ok": False,
                "error": "Gambar tidak dijumpai.",
            }), 404

        liked = session.get("liked_files", [])
        if not isinstance(liked, list):
            liked = []

        liked_set = set(liked)

        if filename in liked_set:
            liked_set.remove(filename)
            image["likes"] = max(0, image["likes"] - 1)
            liked_now = False
        else:
            liked_set.add(filename)
            image["likes"] += 1
            liked_now = True

        session["liked_files"] = list(liked_set)
        simpan_data(records)

    return jsonify({
        "ok": True,
        "likes": image["likes"],
        "liked": liked_now,
    })


@app.route("/comment/<nama_fail>", methods=["POST"])
def komen_gambar(nama_fail):
    filename = os.path.basename(nama_fail)
    payload = request.get_json(silent=True) or request.form

    author = (
        (payload.get("author") or "Anonymous").strip()[:40]
        or "Anonymous"
    )
    text = (payload.get("text") or "").strip()[:300]

    if not text:
        return jsonify({
            "ok": False,
            "error": "Komen tidak boleh kosong.",
        }), 400

    with KUNCI_DATA:
        records = baca_data()
        image = next(
            (item for item in records if item.get("fail") == filename),
            None,
        )

        if not image:
            return jsonify({
                "ok": False,
                "error": "Gambar tidak dijumpai.",
            }), 404

        comment = {
            "id": uuid.uuid4().hex[:8],
            "author": author,
            "text": text,
        }
        image["comments"].append(comment)
        simpan_data(records)

    return jsonify({
        "ok": True,
        "comment": comment,
        "comments": image["comments"],
    })


@app.route("/uploads/<nama_fail>")
def papar_gambar(nama_fail):
    return send_from_directory(
        FOLDER_GAMBAR,
        os.path.basename(nama_fail),
    )


@app.route("/delete", methods=["POST"])
def padam_gambar():
    payload = request.get_json(silent=True) or {}
    filename = os.path.basename(payload.get("fail", ""))

    if not filename:
        return jsonify({
            "ok": False,
            "error": "Nama fail tiada.",
        }), 400

    with KUNCI_DATA:
        records = baca_data()
        target = next(
            (item for item in records if item.get("fail") == filename),
            None,
        )

        if not target:
            return jsonify({
                "ok": False,
                "error": "Gambar tidak dijumpai.",
            }), 404

        (FOLDER_GAMBAR / filename).unlink(missing_ok=True)
        simpan_data([
            item for item in records
            if item.get("fail") != filename
        ])

    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.environ.get("PORT", 5000)),
        debug=False,
    )
