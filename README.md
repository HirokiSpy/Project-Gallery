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
- Optional PIN for protecting individual images from deletion
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

### Windows

```powershell
py -m venv .venv
.venv\Scripts\activate
py -m pip install -r requirements.txt
```

### Linux / macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
```

## Running the Gallery

### Recommended launcher

```bash
python run_galeri.py
```

On Windows, you can also double-click:

```text
start_galeri.bat
```

The launcher asks you to configure credentials on first use, then lets you choose:

1. **Cloudflare Quick Tunnel** — uses a temporary `trycloudflare.com` URL
2. **Cloudflare Zero Trust** — uses a custom domain or tunnel token
3. **Local Only** — available through `http://127.0.0.1:5000`

Use `CTRL+C` to stop the server.

### Windows batch launcher

```powershell
start_website.bat
```

### Direct Flask server

```bash
python app.py
```

Open <http://localhost:5000> in a browser.

`app.py` will create `instance/admin_config.json` automatically only through its first-run setup flow. The recommended approach is to run `run_galeri.py` or `start_website.py`.

## First-Time Setup

When starting the application, you will be prompted to set:

- A gallery passcode of at least 4 characters
- An admin password of at least 8 characters

Both passwords are stored as hashes, and a random Flask secret key is generated locally in:

```text
instance/admin_config.json
```

Existing credentials can be changed when the launcher starts and is given permission to update them.

## Cloudflare Configuration

### Quick Tunnel

Install `cloudflared` and ensure the `cloudflared` command is available in your `PATH`, then select option 1 in `run_galeri.py`.

### Zero Trust

You can enter a domain interactively or provide values through a local `.env` file:

```env
CF_DOMAIN=https://gallery.example.com
CF_TUNNEL_TOKEN=your-tunnel-token
```

Never commit `.env` or tunnel credentials to Git.

## Security

- Gallery access and admin access use separate credentials
- Passwords and image deletion PINs are stored as hashes
- The local configuration file is excluded from version control
- Failed attempts are limited with a 120-second cooldown
- Uploaded filenames are generated securely and restricted to supported image formats
- Request size is limited to 10 MB
- Flask debug mode is disabled
- The application relies on session cookies for gallery and admin access

Keep `instance/`, `uploads/`, `data.json`, and `.env` private when they contain personal or runtime data.

## Data Storage

- `data.json` stores image metadata
- `uploads/` stores uploaded image files
- `instance/admin_config.json` stores password hashes and the Flask secret key
- `instance/tunnel_url.txt` temporarily stores the active public or local URL

## Supported Environment Variables

| Variable | Default | Purpose |
|---|---:|---|
| `PORT` | `5000` | Port used by the Flask server |
| `CF_DOMAIN` | — | Cloudflare Zero Trust custom domain |
| `CF_TUNNEL_TOKEN` | — | Token for starting a Cloudflare tunnel |

## Purpose

This repository is maintained for:

- Practising Python and Flask development
- Exploring web security and authentication concepts
- Experimenting with responsive UI design
- Building and sharing small projects for fun

## License

Unless otherwise stated within a project, the contents of this repository are provided for personal and educational use.

## Author

Created and maintained by [HirokiSpy](https://github.com/HirokiSpy).
