# Project-Gallery

A collection of small projects created for learning, experimentation, and fun.

## About

Project-Gallery is a personal space for building and showcasing lightweight projects. Each project explores different ideas, technologies, or approaches while keeping the scope simple and enjoyable.

## Projects

This repository will continue to grow as new small projects will be added.

## Technologies

The technologies used may vary between projects. Each project may include its own setup and usage instructions.

## Getting Started

### Windows — Run from the Terminal

Open **PowerShell** or **Command Prompt**, then run these commands one by one:

```powershell
git clone https://github.com/HirokiSpy/Project-Gallery.git
cd Project-Gallery
py -m pip install -r requirements.txt
py run_local.py
```

If the `py` command is not available, use `python`:

```powershell
python -m pip install -r requirements.txt
python run_local.py
```

After the terminal asks for an admin password:

1. Enter a new password that is at least 8 characters long.
2. Enter the password again to confirm it.
3. Open your browser and visit <http://localhost:5000>.
4. Press `Ctrl+C` in the terminal to stop the application.

### Linux — Run from the Terminal

Open a terminal and run:

```bash
git clone https://github.com/HirokiSpy/Project-Gallery.git
cd Project-Gallery
python3 -m pip install -r requirements.txt
python3 run_local.py
```

After the terminal asks for an admin password:

1. Enter a new password that is at least 8 characters long.
2. Enter the password again to confirm it.
3. Open your browser and visit <http://localhost:5000>.
4. Press `Ctrl+C` in the terminal to stop the application.

If `pip` or Python packages are restricted by your environment, use a virtual environment:

```bash
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
python run_local.py
```

### Existing Clone

If the project folder already exists:

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

Use this option when you want to share the application over the internet.

1. Install `cloudflared` and make sure the `cloudflared` command is available in the terminal.
2. Run `run_galeri.py`:

**Windows:**

```powershell
py run_galeri.py
```

**Linux:**

```bash
python3 run_galeri.py
```

The script will ask for an admin password, start Flask, and display the Cloudflare Tunnel URL.

## Manual Run

To run Flask without a tunnel:

**Windows:**

```powershell
python app.py
```

**Linux:**

```bash
python3 app.py
```

Then open <http://127.0.0.1:5000>.

To start a Cloudflare Tunnel manually in a second terminal:

```bash
cloudflared tunnel --url http://127.0.0.1:5000
```

## Security Notes

- The admin password is stored as a hash in `instance/admin_config.json`.
- The `instance/` folder is not included in Git.
- Do not share or commit the configuration file.
- Gallery images and records are stored locally in `uploads/` and `data.json`.
- Do not commit local images or runtime data to the repository.
- Flask debug mode is disabled to prevent internal application details from being exposed.

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
