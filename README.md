# Project-Gallery

A collection of small projects created for learning, experimentation, and fun.

## About

Project-Gallery is a personal space for building and showcasing lightweight projects. Each project explores different ideas, technologies, or approaches while keeping the scope simple and enjoyable.

## Projects

This repository will continue to grow as new small projects are added.

## Technologies

The technologies used may vary between projects. Each project may include its own setup and usage instructions.

## Getting Started

```bash
git clone https://github.com/HirokiSpy/Project-Gallery.git
cd Project-Gallery
```

Open individual project folders to view their source code and instructions.

## Usage

### Automatic Run — Cloudflare Tunnel

Run locally and expose the web application through a Cloudflare domain.

On Windows and Linux:

```bash
python run_galeri.py
```

On Windows only, you can double-click:

```text
start_galeri.bat
```

### Manual Run

1. Open a terminal and navigate to the project folder:

```bash
cd path/to/project
```

2. Start the application:

```bash
python app.py
```

3. Open a new terminal and create a Cloudflare Tunnel:

```bash
cloudflared tunnel --url http://localhost:5000
```

Cloudflare Tunnel will provide a public URL that can be used to access the application.

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
