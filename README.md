# Project-Gallery

A collection of small projects created for learning, experimentation, and fun.

## About

Project-Gallery is a personal space for building and showcasing lightweight projects. Each project explores different ideas, technologies, or approaches while keeping the scope simple and enjoyable.

## Projects

This repository will continue to grow as new small projects are added.

## Technologies

The technologies used may vary between projects. Each project may include its own setup and usage instructions.

## Getting Started

### Windows — jalankan terus daripada Terminal

Buka **PowerShell** atau **Command Prompt**, kemudian jalankan arahan ini satu demi satu:

```powershell
git clone https://github.com/HirokiSpy/Project-Gallery.git
cd Project-Gallery
py -m pip install -r requirements.txt
py run_local.py
```

Jika arahan `py` tidak tersedia, gunakan `python`:

```powershell
python -m pip install -r requirements.txt
python run_local.py
```

Selepas terminal meminta kata laluan admin:

1. Masukkan kata laluan baharu sekurang-kurangnya 12 aksara.
2. Masukkan semula kata laluan untuk pengesahan.
3. Buka browser dan pergi ke <http://127.0.0.1:5000>.
4. Tekan `Ctrl+C` dalam terminal untuk menghentikan aplikasi.

### Linux — jalankan terus daripada Terminal

Buka terminal, kemudian jalankan:

```bash
git clone https://github.com/HirokiSpy/Project-Gallery.git
cd Project-Gallery
python3 -m pip install -r requirements.txt
python3 run_local.py
```

Selepas terminal meminta kata laluan admin:

1. Masukkan kata laluan baharu sekurang-kurangnya 12 aksara.
2. Masukkan semula kata laluan untuk pengesahan.
3. Buka browser dan pergi ke <http://127.0.0.1:5000>.
4. Tekan `Ctrl+C` dalam terminal untuk menghentikan aplikasi.

Jika `pip` atau modul Python dipasang dalam persekitaran yang dikawal, gunakan persekitaran maya:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_local.py
```

### Klon yang telah wujud

Jika folder projek sudah ada:

**Windows:**

```powershell
cd Project-Gallery
py run_local.py
```

**Linux:**

```bash
cd Project-Gallery
python3 run_local.py
```

## Automatic Run — Cloudflare Tunnel

Gunakan hanya jika ingin berkongsi aplikasi kepada orang lain melalui internet.

1. Pasang `cloudflared` dan pastikan arahan `cloudflared` tersedia dalam terminal.
2. Jalankan `run_galeri.py`:

**Windows:**

```powershell
py run_galeri.py
```

**Linux:**

```bash
python3 run_galeri.py
```

Script akan meminta kata laluan admin, memulakan Flask, dan kemudian memaparkan URL Cloudflare Tunnel.

## Manual Run

Untuk menjalankan Flask tanpa tunnel:

```bash
python app.py
```

Atau:

```bash
python3 app.py
```

Buka <http://127.0.0.1:5000>.

Untuk membina Cloudflare Tunnel secara manual dalam terminal kedua:

```bash
cloudflared tunnel --url http://127.0.0.1:5000
```

## Security Notes

- Kata laluan admin disimpan sebagai hash dalam `instance/admin_config.json`.
- Folder `instance/` tidak dimasukkan ke dalam Git.
- Jangan kongsi fail konfigurasi itu dengan sesiapa.
- Gambar dan rekod galeri disimpan secara lokal dalam folder `uploads/` dan `data.json`.
- Jangan commit gambar atau data lokal ke repo.
- Flask debug dimatikan supaya maklumat dalaman tidak didedahkan.

## Purpose

This repository is maintained for:

- Practising development skills
- Trying out new ideas
- Experimenting with small applications
- Having fun while learning

## License

Unless otherwise stated within a project, the contents of this repository are provided for personal and educational use.

## Author

Created and maintained by [HirokiSpy](https://github.com/HirokiSpy).
