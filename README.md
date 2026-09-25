# LITT

LITT (Lyrics in the Terminal) is, as the name suggests, a way to display lyrics of the currently playing song in the terminal.
Note that this tool currently only supports linux as it uses playerctl but it may be expanded to multiple operating systems in the future.

## Usage
Firstly make sure playerctl is installed:
```bash
# Debian / Debian-based
sudo apt install playerctl

# Fedora / Fedora-based
sudo dnf install playerctl

# Arch / Arch-based
sudo pacman -S playerctl
```

You can run LITT by typing `litt` and then choose your playerctl source.
To access the settings run `litt --settings`.

## Installation

The following commands will automatically install uv and LITT
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install litt
```

## Building

Prerequisites
- python (with pip)
- git/(gh)

1. Clone GitHub repository
```bash
git clone https://github.com/FabBeyond/litt.git
cd litt
```

2. Set up a virtual environment
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

3. Run the program
```bash
python3 src/main.py
```
