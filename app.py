import os
import json
import time
from flask import Flask, request, render_template, send_from_directory, redirect, jsonify, session
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'galeri-gambar-hiroki-secret-key')

# Kata laluan profil Admin
ADMIN_PASSWORD = os.environ.get('ADMIN_PASSWORD', 'hiroki1033')

# Status admin online untuk dilihat semua orang
admin_online = False

# Tetapan folder dan fail database ringkas
FOLDER_GAMBAR = 'uploads'
FAIL_DATA = 'data.json'

os.makedirs(FOLDER_GAMBAR, exist_ok=True)

if not os.path.exists(FAIL_DATA):
    with open(FAIL_DATA, 'w', encoding='utf-8') as f:
        json.dump([], f)


def baca_data():
    with open(FAIL_DATA, 'r', encoding='utf-8') as f:
        return json.load(f)


def simpan_data(data):
    with open(FAIL_DATA, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


@app.route('/', methods=['GET', 'POST'])
def utama():
    if request.method == 'POST':
        nama_pengirim = (request.form.get('nama') or 'Tanpa Nama').strip()[:40]
        pin_padam = (request.form.get('pin') or '').strip()
        warna_nama = (request.form.get('warna_nama') or '#c084fc').strip()
        fail = request.files.get('gambar')

        if fail and fail.filename != '':
            nama_selamat = f"{int(time.time())}_{secure_filename(fail.filename)}"
            fail.save(os.path.join(FOLDER_GAMBAR, nama_selamat))

            rekod = baca_data()
            rekod.insert(0, {
                'nama': nama_pengirim,
                'fail': nama_selamat,
                'ada_pin': bool(pin_padam),
                'pin': pin_padam,
                'warna': warna_nama,
            })
            simpan_data(rekod)

        return redirect('/')

    senarai_data = baca_data()
    is_admin = bool(session.get('is_admin'))
    return render_template(
        'index.html',
        senarai_data=senarai_data,
        is_admin=is_admin,
        admin_online=admin_online,
    )


@app.route('/admin/login', methods=['POST'])
def admin_login():
    global admin_online
    data = request.get_json(silent=True) or {}
    katalaluan = (data.get('password') or request.form.get('password') or '').strip()

    if katalaluan == ADMIN_PASSWORD:
        session['is_admin'] = True
        admin_online = True
        return jsonify({'ok': True, 'is_admin': True, 'admin_online': True})

    return jsonify({'ok': False, 'error': 'Kata laluan admin salah.'}), 401


@app.route('/admin/logout', methods=['POST'])
def admin_logout():
    global admin_online
    session.pop('is_admin', None)
    admin_online = False
    return jsonify({'ok': True, 'is_admin': False, 'admin_online': False})


@app.route('/admin/status')
def admin_status():
    return jsonify({'admin_online': admin_online})


@app.route('/uploads/<nama_fail>')
def papar_gambar(nama_fail):
    nama_bersih = os.path.basename(nama_fail)
    return send_from_directory(FOLDER_GAMBAR, nama_bersih)


@app.route('/delete', methods=['POST'])
def padam_gambar():
    data = request.get_json(silent=True) or {}
    nama_fail = os.path.basename(data.get('fail', ''))
    pin_diberi = (data.get('pin') or '').strip()
    is_admin = bool(session.get('is_admin'))

    if not nama_fail:
        return jsonify({'ok': False, 'error': 'Nama fail tiada.'}), 400

    rekod = baca_data()
    item_padam = next((item for item in rekod if item.get('fail') == nama_fail), None)

    if not item_padam:
        return jsonify({'ok': False, 'error': 'Rekod gambar tidak dijumpai.'}), 404

    if not is_admin:
        pin_tersimpan = (item_padam.get('pin') or '').strip()
        if not pin_tersimpan:
            return jsonify({'ok': False, 'error': 'Gambar ini tiada PIN dan tidak boleh dipadam.'}), 403

        if pin_diberi != pin_tersimpan:
            return jsonify({'ok': False, 'error': 'PIN salah! Gambar tidak dipadam.'}), 403

    laluan_fail = os.path.join(FOLDER_GAMBAR, nama_fail)
    if os.path.exists(laluan_fail):
        os.remove(laluan_fail)

    rekod_baru = [item for item in rekod if item.get('fail') != nama_fail]
    simpan_data(rekod_baru)

    return jsonify({'ok': True})


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)