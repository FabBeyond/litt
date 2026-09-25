# LITT

LITT (Lyrics in the Terminal) is, as the name suggests, a way to display lyrics of the currently playing song in the terminal.
Note that this tool currently only supports linux as it uses playerctl but it may be expanded to multiple operating systems in the future.

## Usage
You can run LITT by typing `litt` and then choose your playerctl source.
To access the settings run `litt --settings`.

## Installation

This tool is currently in development and has no official release but you can try out the bleeding edge version by building it yourself with the steps below.

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
