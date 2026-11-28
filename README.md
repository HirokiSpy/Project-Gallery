# Project-Gallery

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)
![HTML](https://img.shields.io/badge/HTML-E34F26?style=flat&logo=html5&logoColor=white)

A simple Flask and HTML image gallery. This project uses local JSON files and folders without a third-party database.

## Features

- Separate gallery passcode and admin password
- Hashed gallery, admin and image PIN passwords
- PNG, JPG, JPEG, GIF and WebP uploads up to 10 MB
- Custom uploader names and name colours
- Optional PIN protection for deleting images
- Responsive gallery layout and image lightbox
- Terminal-based visitor monitor
- Admin online status indicator
- Failed-login rate limiting and temporary cooldown
- Quick Tunnel, Zero Trust or local-only modes
- HTTP/HTTPS-aware session cookie configuration
- Flask debug mode disabled during normal startup

## Project Structure

```text
Project-Gallery/
├── app.py                 # Flask application and routes
├── security_config.py     # Password configuration and secret key setup
├── run_galeri.py          # Main launcher with connection options
├── start_website.py       # Alternative Python launcher
├── start_galeri.bat       # Windows launcher for run_galeri.py
├── start_website.bat      # Windows launcher for start_website.py
├── templates/
│   └── index.html         # Gallery interface and JavaScript
├── uploads/               # Uploaded image files
├── data.json              # Gallery metadata in JSON format
├── requirements.txt       # Python dependencies
├── .env.example           # Example environment variables
└── .gitignore
```

## Requirements

- Python 3.10 or newer
- `pip`
- Cloudflared only for public Cloudflare connections

## Installation

```bash
git clone https://github.com/HirokiSpy/Project-Gallery.git
cd Project-Gallery
```

### Windows

```powershell
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
```

### Linux or macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Getting Started

Recommended launcher:

```bash
python run_galeri.py
```

On Windows, you can also open `start_galeri.bat`.

Alternatively, start the Flask server directly:

```bash
python app.py
```

Then open:

```text
http://127.0.0.1:5000
```

On the first run, the launcher asks for:

- A gallery passcode of at least 4 characters
- An admin password of at least 8 characters

Both passwords are stored as hashes. A random Flask secret key is generated locally.

## Connection Modes

`run_galeri.py` and `start_website.py` provide three modes:

1. **Quick Tunnel** — creates a temporary `trycloudflare.com` URL
2. **Zero Trust** — uses a Cloudflare domain or tunnel token
3. **Local Only** — allows access through localhost or the local network

For Zero Trust, copy `.env.example` to `.env`:

```env
CF_DOMAIN=https://your-domain.example
CF_TUNNEL_TOKEN=your-tunnel-token
PORT=5000
GALLERY_HTTPS=1
```

Do not commit `.env` or tunnel credentials to the repository.

## Data Storage

This project deliberately uses local files instead of a third-party database:

- `data.json` stores metadata such as uploader name, filename and colour
- `uploads/` stores uploaded image files
- `instance/admin_config.json` stores password hashes and the Flask secret key
- `instance/tunnel_url.txt` stores the temporary tunnel or local URL

`data.json` is protected by a local read/write lock. Writes use a temporary `data.json.tmp` file before atomically replacing the main file.

## Upload Validation

Uploads must meet these requirements:

- Filename extension must be PNG, JPG, JPEG, GIF or WebP
- MIME type must start with `image/`
- Request size must not exceed 10 MB
- Filenames are generated randomly using UUID
- Name colours must use six-character HEX format, such as `#c084fc`

For public or untrusted use, validating the actual image contents with an image library is recommended.

## Visitor IP Handling

The server obtains an IPv4 address from:

1. `request.remote_addr`
2. A validated `CF-Connecting-IP` header

The `/log-ip` endpoint does not accept an IP address directly from the request body. IPv4 values are validated before being stored in the session or displayed by the visitor monitor.

## Security and Limitations

- Passwords and PINs are not stored as plain text
- Failed login attempts are limited with a 120-second cooldown
- Uploaded filenames are sanitised and replaced with UUID names
- Session cookies use `HTTPONLY` and `SAMESITE=Lax`
- Secure cookies can be enabled with `GALLERY_HTTPS=1` when using HTTPS
- Runtime files, secrets and user data are excluded by `.gitignore`
- JSON operations are protected against overlapping writes within one process
- High-scale or multi-process deployment would require external coordination or a database

## Git-Ignored Files

The following files and folders should not be committed:

- `.env`
- `instance/`
- `data.json`
- `data.json.tmp`
- `uploads/*`, except `.gitkeep`
- `.venv/` or `venv/`
- Python cache files

## Purpose

- Practising Python and Flask development
- Learning authentication and session handling
- Experimenting with responsive user interfaces
- Building small projects for personal learning and use

## License

Provided for personal and educational use.

## Author

Built and maintained by [HirokiSpy](https://github.com/HirokiSpy).
