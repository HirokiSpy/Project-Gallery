# Project-Gallery

![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![Flask](https://img.shields.io/badge/Flask-000000?style=flat&logo=flask&logoColor=white)
![HTML](https://img.shields.io/badge/HTML-E34F26?style=flat&logo=html5&logoColor=white)

A secure, responsive image gallery built with Flask. The project is maintained for learning, experimentation, and fun.

## Features

- Gallery passcode lock screen
- Separate admin password and admin mode
- Password hashing for gallery, admin, and per-image PIN protection
- Upload support for PNG, JPG, JPEG, GIF, and WebP images (maximum 10 MB)
- Custom uploader name and name colour
- Responsive desktop and mobile gallery layout
- Lightbox image viewer
- Live visitor monitor in the terminal
- Admin online status indicator
- Failed-login rate limiting and temporary cooldown
- Cloudflare Quick Tunnel, Zero Trust, and local-only modes
- Debug mode disabled in normal server startup

## Project Structure

```text
Project-Gallery/
├── app.py                 # Flask application and routes
├── security_config.py     # Local password setup and configuration loading
├── run_galeri.py          # Recommended launcher with tunnel selection
├── start_website.py       # Python launcher for local/tunnel modes
├── start_galeri.bat       # Windows launcher for the tunnel/menu mode
├── start_website.bat      # Windows launcher for the website
├── templates/
│   └── index.html         # Gallery interface and frontend logic
├── uploads/               # Uploaded image files
├── data.json              # Gallery metadata
├── requirements.txt       # Python dependencies
└── .gitignore
```

## Requirements

- Python 3.10 or newer
- `pip`
- `cloudflared` only if using a public tunnel

## Installation

Clone the repository:

```bash
git clone https://github.com/HirokiSpy/Project-Gallery.git
cd Project-Gallery
```

Create and activate a virtual environment (recommended):

```powershell
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
```

Linux / macOS:

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install -r requirements.txt
```

## Running

```bash
python run_galeri.py
```

The launcher asks for credentials on first use, then offers local, Quick Tunnel, or Zero Trust modes.

## Storage

This project intentionally uses simple local files without a third-party database:

- `data.json` stores gallery metadata.
- `uploads/` stores uploaded image files.
- `instance/admin_config.json` stores credential hashes and the Flask secret key.
- `instance/tunnel_url.txt` temporarily stores the active tunnel or local URL.

Operations that read or change `data.json` are serialized with a local lock, and writes use an atomic temporary file.

## IP Address Handling

The server derives visitor IPv4 from `request.remote_addr` or the validated `CF-Connecting-IP` header. `/log-ip` no longer accepts a user-supplied IP address.

## Upload Validation

Uploads must:

- use a supported filename extension;
- declare an image MIME type;
- remain within the 10 MB request limit.

## Purpose

- Practising Python and Flask development
- Exploring web security and authentication concepts
- Experimenting with responsive UI design
- Building small projects for fun

## License

Provided for personal and educational use.

## Author

Created and maintained by [HirokiSpy](https://github.com/HirokiSpy).
