import hmac
import ipaddress
import json
import logging
import os
import re
import threading
import time
import uuid
from datetime import datetime
from pathlib import Path

from flask import Flask, jsonify, redirect, render_template, request, send_from_directory, session
from rich.console import Console
from rich.table import Table
from werkzeug.middleware.proxy_fix import ProxyFix
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from security_config import configure_admin_password, load_config

BASE_DIR = Path(__file__).resolve().parent
URL_FILE = BASE_DIR / "instance" / "tunnel_url.txt"

if __name__ == "__main__" and os.environ.get("GALLERY_CONFIG_READY") != "1":
    configure_admin_password()
CONFIG = load_config()

logging.getLogger("werkzeug").setLevel(logging.ERROR)

app = Flask(__name__)
app.wsgi_app = ProxyFix(app.wsgi_app, x_for=1, x_proto=1, x_host=1, x_prefix=1)
app.secret_key = CONFIG["secret_key"]
app.config.update(
    SESSION_COOKIE_HTTPONLY=True,
    SESSION_COOKIE_SAMESITE="Lax",
    SESSION_COOKIE_SECURE=os.environ.get("GALLERY_HTTPS", "0") == "1",
    MAX_CONTENT_LENGTH=10 * 1024 * 1024,
)

admin_online = False
FOLDER_GAMBAR = BASE_DIR / "uploads"
FAIL_DATA = BASE_DIR / "data.json"
EXTENSIONS_GAMBAR = {"png", "jpg", "jpeg", "gif", "webp"}
KUNCI_DATA = threading.RLock()
FOLDER_GAMBAR.mkdir(exist_ok=True)
with KUNCI_DATA:
    if not FAIL_DATA.exists():
        FAIL_DATA.write_text("[]", encoding="utf-8")

pelawat_aktif = {}
kunci_jadual = threading.Lock()
console = Console(force_terminal=True)

CUBAAAN_GAGAL = {}
KUNCI_RATE = threading.Lock()
HAD_CUBAAN = 5
TEMPOH_SEKAT = 120
TEMPOH_PELAWAT_TIDAK_AKTIF = 15 * 60
WARNA_HEX = re.compile(r"^#[0-9A-Fa-f]{6}$")


def dapatkan_kunci_klien():
    return dapatkan_ipv4_pelayan() or request.remote_addr or "unknown"


def sahkan_ipv4(value):
    if not value:
        return None
    value = value.strip()
    try:
        obj = ipaddress.ip_address(value)
        return value if obj.version == 4 else None
    except ValueError:
        return None


def bersihkan_pelawat_tidak_aktif():
    sekarang = time.time()
    with kunci_jadual:
        tamat = [
            key for key, info in pelawat_aktif.items()
            if sekarang - info.get("timestamp", sekarang) > TEMPOH_PELAWAT_TIDAK_AKTIF
        ]
        for key in tamat:
            pelawat_aktif.pop(key, None)


def disekat_sekarang(kunci_jenis: str) -> int:
    kunci = f"{kunci_jenis}:{dapatkan_kunci_klien()}"
    sekarang = time.time()
    with KUNCI_RATE:
        rekod = CUBAAAN_GAGAL.get(kunci)
        if not rekod:
            return 0
        if rekod["sekat_hingga"] > sekarang:
            return int(rekod["sekat_hingga"] - sekarang)
        if rekod["sekat_hingga"] != 0:
            CUBAAAN_GAGAL.pop(kunci, None)
        return 0


def rekod_cubaan_gagal(kunci_jenis: str):
    kunci = f"{kunci_jenis}:{dapatkan_kunci_klien()}"
    sekarang = time.time()
    with KUNCI_RATE:
        rekod = CUBAAAN_GAGAL.setdefault(kunci, {"bil": 0, "sekat_hingga": 0})
        rekod["bil"] += 1
        if rekod["bil"] >= HAD_CUBAAN:
            rekod["sekat_hingga"] = sekarang + TEMPOH_SEKAT
            rekod["bil"] = 0


def reset_cubaan(kunci_jenis: str):
    kunci = f"{kunci_jenis}:{dapatkan_kunci_klien()}"
    with KUNCI_RATE:
        CUBAAAN_GAGAL.pop(kunci, None)


def baca_url_tunnel():
    try:
        if URL_FILE.exists():
            url = URL_FILE.read_text(encoding="utf-8").strip()
            if url:
                return url
    except OSError:
        pass
    return "http://127.0.0.1:5000"


def bina_jadual():
    bersihkan_pelawat_tidak_aktif()
    url_semasa = baca_url_tunnel()
    jadual = Table(
        title=f"Live Visitor Monitor - CoreMemories\nPublic URL: [bold cyan]{url_semasa}[/bold cyan]",
        border_style="bright_magenta",
    )
    jadual.add_column("No.", justify="center", style="cyan", no_wrap=True)
    jadual.add_column("IPv4", style="green", no_wrap=True)
    jadual.add_column("Device Name", style="yellow")
    jadual.add_column("Page / Activity", style="white")
    jadual.add_column("Time", justify="center", style="dim")

    with kunci_jadual:
        if not pelawat_aktif:
            jadual.add_row("-", "Waiting...", "-", "No active visitors yet", "-")
        else:
            for idx, (vid, info) in enumerate(pelawat_aktif.items(), start=1):
                jadual.add_row(
                    str(idx), info["ipv4"], info["device"],
                    info["aktiviti"], info["masa"],
                )
    return jadual


def dapatkan_id_pelawat():
    if "visitor_id" not in session:
        session["visitor_id"] = uuid.uuid4().hex[:12]
    return session["visitor_id"]


def kemaskini_pelawat(visitor_id, ipv4, device, aktiviti):
    masa_sekarang = datetime.now().strftime("%H:%M:%S")
    timestamp = time.time()
    with kunci_jadual:
        if visitor_id not in pelawat_aktif:
            pelawat_aktif[visitor_id] = {
                "ipv4": ipv4 or "Detecting...", "device": device,
                "aktiviti": aktiviti, "masa": masa_sekarang,
                "timestamp": timestamp,
            }
        else:
            if ipv4 and ipv4 not in {"Detecting...", "None", "IPv6/Tunnel"}:
                pelawat_aktif[visitor_id]["ipv4"] = ipv4
            pelawat_aktif[visitor_id].update({
                "device": device, "aktiviti": aktiviti,
                "masa": masa_sekarang, "timestamp": timestamp,
            })


def baca_data():
    with KUNCI_DATA:
        try:
            with FAIL_DATA.open("r", encoding="utf-8") as f:
                data = json.load(f)
            return data if isinstance(data, list) else []
        except (OSError, json.JSONDecodeError):
            return []


def simpan_data(data):
    with KUNCI_DATA:
        sementara = FAIL_DATA.with_suffix(".tmp")
        with sementara.open("w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=4)
            f.flush()
            os.fsync(f.fileno())
        sementara.replace(FAIL_DATA)


def sahkan_pin(pin_diberi, item):
    pin_hash = item.get("pin_hash", "")
    if pin_hash:
        try:
            return check_password_hash(pin_hash, pin_diberi)
        except (ValueError, TypeError):
            return False
    pin_lama = item.get("pin", "")
    if pin_lama and hmac.compare_digest(pin_diberi, pin_lama):
        return True
    return False


def dapatkan_nama_device():
    user_agent = request.headers.get("User-Agent", "")
    if "iPhone" in user_agent:
        return "iPhone (iOS)"
    if "iPad" in user_agent:
        return "iPad (iPadOS)"
    if "Android" in user_agent:
        mula = user_agent.find("(")
        tamat = user_agent.find(")", mula)
        if mula != -1 and tamat != -1:
            return f"Android ({user_agent[mula + 1:tamat]})"
        return "Android"
    if "Windows" in user_agent:
        return "PC (Windows)"
    if "Macintosh" in user_agent:
        return "Mac (macOS)"
    if "Linux" in user_agent:
        return "PC (Linux) / Mobile Desktop Mode"
    return user_agent[:45] or "Unknown Device"


def dapatkan_ipv4_pelayan():
    remote_ip = sahkan_ipv4(request.remote_addr)
    if remote_ip:
        return remote_ip
    cf_ip = sahkan_ipv4(request.headers.get("CF-Connecting-IP", ""))
    if cf_ip:
        return cf_ip
    return None


def ada_akses_galeri() -> bool:
    return bool(session.get("gallery_unlocked") or session.get("is_admin"))


@app.before_request
def kawalan_pintu_masuk():
    laluan_bebas = {"/", "/unlock", "/log-ip"}
    if request.path in laluan_bebas:
        return None
    if not ada_akses_galeri():
        if request.path.startswith("/uploads/"):
            return "Akses disekat. Sila masukkan kata laluan galeri.", 403
        return jsonify({"ok": False, "error": "Sesi terkunci. Sila masukkan kata laluan galeri dahulu."}), 403
    return None


@app.route("/unlock", methods=["POST"])
def buka_kunci_galeri():
    vid = dapatkan_id_pelawat()
    ipv4 = session.get("client_ipv4") or dapatkan_ipv4_pelayan() or "Detecting..."
    device = dapatkan_nama_device()
    baki_sekat = disekat_sekarang("unlock")
    if baki_sekat > 0:
        return jsonify({"ok": False, "error": f"Terlalu banyak cubaan salah. Cuba semula dalam {baki_sekat} saat."}), 429
    data = request.get_json(silent=True) or {}
    passcode = (data.get("passcode") or request.form.get("passcode") or "").strip()
    if check_password_hash(CONFIG["gallery_passcode_hash"], passcode):
        reset_cubaan("unlock")
        session["gallery_unlocked"] = True
        kemaskini_pelawat(vid, ipv4, device, "Gallery Unlocked")
        return jsonify({"ok": True})
    rekod_cubaan_gagal("unlock")
    kemaskini_pelawat(vid, ipv4, device, "Unlock Failed (Wrong Passcode)")
    return jsonify({"ok": False, "error": "Kata laluan galeri salah."}), 401


@app.route("/lock", methods=["POST"])
def kunci_galeri_semula():
    global admin_online
    vid = dapatkan_id_pelawat()
    ipv4 = session.get("client_ipv4") or dapatkan_ipv4_pelayan() or "Detecting..."
    device = dapatkan_nama_device()
    if session.get("is_admin"):
        admin_online = False
    session.clear()
    session["visitor_id"] = vid
    session["client_ipv4"] = ipv4
    kemaskini_pelawat(vid, ipv4, device, "Locked / Left Gallery")
    return jsonify({"ok": True})


@app.route("/log-ip", methods=["POST"])
def log_ipv4():
    vid = dapatkan_id_pelawat()
    ipv4_baru = dapatkan_ipv4_pelayan() or session.get("client_ipv4") or "Detecting..."
    if sahkan_ipv4(ipv4_baru):
        session["client_ipv4"] = ipv4_baru
    device = dapatkan_nama_device()
    status_laman = "Home Page" if ada_akses_galeri() else "Lock Screen"
    kemaskini_pelawat(vid, ipv4_baru, device, status_laman)
    return jsonify({"ok": True})


@app.route("/", methods=["GET", "POST"])
def utama():
    vid = dapatkan_id_pelawat()
    ipv4 = session.get("client_ipv4") or dapatkan_ipv4_pelayan() or "Detecting..."
    device = dapatkan_nama_device()
    if not ada_akses_galeri():
        kemaskini_pelawat(vid, ipv4, device, "Lock Screen")
        return render_template("index.html", unlocked=False, senarai_data=[], is_admin=False, admin_online=False)

    if request.method == "POST":
        nama_pengirim = (request.form.get("nama") or "Tanpa Nama").strip()[:40]
        pin_padam = (request.form.get("pin") or "").strip()
        warna_nama = (request.form.get("warna_nama") or "#c084fc").strip()
        if not WARNA_HEX.fullmatch(warna_nama):
            warna_nama = "#c084fc"
        fail = request.files.get("gambar")
        if fail and fail.filename:
            nama_asal = secure_filename(fail.filename)
            sambungan = Path(nama_asal).suffix.lstrip(".").lower()
            if not sambungan or sambungan not in EXTENSIONS_GAMBAR:
                return "Jenis fail gambar tidak disokong.", 400
            if not fail.mimetype or not fail.mimetype.startswith("image/"):
                return "Kandungan fail bukan imej.", 400
            nama_selamat = f"{uuid.uuid4().hex}.{sambungan}"
            laluan_baru = FOLDER_GAMBAR / nama_selamat
            fail.save(laluan_baru)
            with KUNCI_DATA:
                rekod = baca_data()
                rekod.insert(0, {
                    "nama": nama_pengirim, "fail": nama_selamat,
                    "ada_pin": bool(pin_padam),
                    "pin_hash": generate_password_hash(pin_padam) if pin_padam else "",
                    "warna": warna_nama,
                })
                try:
                    simpan_data(rekod)
                except OSError:
                    laluan_baru.unlink(missing_ok=True)
                    return "Gagal menyimpan rekod gambar.", 500
            kemaskini_pelawat(vid, ipv4, device, f"Uploaded Image ('{nama_pengirim}')")
        return redirect("/")

    kemaskini_pelawat(vid, ipv4, device, "Home Page")
    senarai_data = baca_data()
    return render_template("index.html", unlocked=True, senarai_data=senarai_data,
                           is_admin=bool(session.get("is_admin")), admin_online=admin_online)


@app.route("/admin/login", methods=["POST"])
def admin_login():
    global admin_online
    vid = dapatkan_id_pelawat()
    ipv4 = session.get("client_ipv4") or dapatkan_ipv4_pelayan() or "Detecting..."
    device = dapatkan_nama_device()
    baki_sekat = disekat_sekarang("admin")
    if baki_sekat > 0:
        return jsonify({"ok": False, "error": f"Terlalu banyak cubaan admin gagal. Cuba lagi dalam {baki_sekat} saat."}), 429
    data = request.get_json(silent=True) or {}
    katalaluan = (data.get("password") or request.form.get("password") or "").strip()
    if check_password_hash(CONFIG["admin_password_hash"], katalaluan):
        reset_cubaan("admin")
        session.clear()
        session["visitor_id"] = vid
        session["gallery_unlocked"] = True
        session["is_admin"] = True
        session["client_ipv4"] = ipv4
        admin_online = True
        kemaskini_pelawat(vid, ipv4, device, "Admin Login (SUCCESS)")
        return jsonify({"ok": True, "is_admin": True, "admin_online": True})
    rekod_cubaan_gagal("admin")
    kemaskini_pelawat(vid, ipv4, device, "Admin Login (FAILED)")
    return jsonify({"ok": False, "error": "Kata laluan admin salah."}), 401


@app.route("/admin/logout", methods=["POST"])
def admin_logout():
    global admin_online
    vid = dapatkan_id_pelawat()
    ipv4 = session.get("client_ipv4") or dapatkan_ipv4_pelayan() or "Detecting..."
    device = dapatkan_nama_device()
    session.clear()
    session["visitor_id"] = vid
    session["gallery_unlocked"] = True
    session["client_ipv4"] = ipv4
    admin_online = False
    kemaskini_pelawat(vid, ipv4, device, "Admin Logout")
    return jsonify({"ok": True, "is_admin": False, "admin_online": False})


@app.route("/admin/status")
def admin_status():
    return jsonify({"admin_online": admin_online})


@app.route("/uploads/<nama_fail>")
def papar_gambar(nama_fail):
    return send_from_directory(FOLDER_GAMBAR, os.path.basename(nama_fail))


@app.route("/delete", methods=["POST"])
def padam_gambar():
    vid = dapatkan_id_pelawat()
    ipv4 = session.get("client_ipv4") or dapatkan_ipv4_pelayan() or "Detecting..."
    device = dapatkan_nama_device()
    data = request.get_json(silent=True) or {}
    nama_fail = os.path.basename(data.get("fail", ""))
    pin_diberi = (data.get("pin") or "").strip()
    is_admin = bool(session.get("is_admin"))
    if not nama_fail:
        return jsonify({"ok": False, "error": "Nama fail tiada."}), 400

    with KUNCI_DATA:
        rekod = baca_data()
        item_padam = next((item for item in rekod if item.get("fail") == nama_fail), None)
        if not item_padam:
            return jsonify({"ok": False, "error": "Rekod gambar tidak dijumpai."}), 404
        if not is_admin:
            if not (item_padam.get("pin_hash") or item_padam.get("pin")):
                return jsonify({"ok": False, "error": "Gambar ini tiada PIN dan tidak boleh dipadam."}), 403
            if not sahkan_pin(pin_diberi, item_padam):
                kemaskini_pelawat(vid, ipv4, device, f"Delete Failed ('{item_padam.get('nama', '')}')")
                return jsonify({"ok": False, "error": "PIN salah! Gambar tidak dipadam."}), 403

        laluan_fail = FOLDER_GAMBAR / nama_fail
        if laluan_fail.exists():
            laluan_fail.unlink()
        rekod_baru = [item for item in rekod if item.get("fail") != nama_fail]
        simpan_data(rekod_baru)

    kemaskini_pelawat(vid, ipv4, device, f"Deleted Image ('{item_padam.get('nama', '')}')")
    return jsonify({"ok": True})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=False)
