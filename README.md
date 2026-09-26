# LITT

LITT (Lyrics in the Terminal) is, as the name suggests, a way to display lyrics of the currently playing song in the terminal.
Note that this tool currently only supports linux as it uses playerctl but it may be expanded to multiple operating systems in the future.

## Requirements
- Linux
- playerctl

Install playerctl with our distros package manager:
```bash
# Debian / Debian-based
sudo apt install playerctl

# Fedora / Fedora-based
sudo dnf install playerctl

# Arch / Arch-based
sudo pacman -S playerctl
```

## Installation

The following commands will automatically install uv and LITT
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
uv tool install litt
```

## Usage
To use LITT start any song (Spotify/YouTube) and run `litt`
LITT will then list currently playing sources and you can choose one.

To access the settings run `litt --settings`
The setings include:
- Font Size
- Custom Font
- Text Style

### Keybinds
The following keybinds can be used:
```txt
, - Decrease Lyrics Size
. - Increase Lyrics Size
r - Re-fetch Lyrics
q - Quit
```

## Building from source

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
python3 src/litt/main.py
```

## Credits
- [syncedlyrics](https://pypi.org/project/syncedlyrics/)
- [Noto-CJK](https://github.com/notofonts/noto-cjk/)
