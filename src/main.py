from rich.console import Console
from rich.align import Align
from rich.text import Text
from PIL import Image, ImageDraw, ImageFont
from simple_term_menu import TerminalMenu
import syncedlyrics
import pyfiglet
import time
from requests.exceptions import RequestException
from datetime import datetime
import subprocess
import sys
import argparse
import re
import os
import json

def cmd(command):
    return subprocess.run(command, capture_output=True, text=True)

if subprocess.run(["which", "playerctl"], capture_output=True, text=True).returncode != 0:
    print("Playerctl isnt installed or added to PATH")
    sys.exit(1)
if cmd(["playerctl", "-l"]).stdout.strip() == "":
    print("No playerctl source")
    sys.exit(1)

settings = {}
config_dir = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
config_path = os.path.join(config_dir, "litt")
config_file = os.path.join(config_path, "config.json")
DEFAULTS = {"font": "base", "font_style": "blocky"}
os.makedirs(config_path, exist_ok=True)
if not os.path.isfile(config_file):
    with open(config_file, "w") as f:
        json.dump(DEFAULTS, f, indent=2)
with open(config_file) as f:
    settings = {**DEFAULTS, **json.load(f)}

parser = argparse.ArgumentParser("LITT")
parser.add_argument("--settings", action="store_true")
args = parser.parse_args()
if args.settings:
    import settings
    sys.exit(1)

TOKEN_RE = re.compile(
    r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f\uac00-\ud7a3]'
    r'|\s+'
    r'|\S+'
)

console = Console()
players = subprocess.run(["playerctl", "-l"], capture_output=True, text=True).stdout.strip()
players = players.split("\n")
player_menu = TerminalMenu(players, title="Choose your playerctl source:")
selected_player = player_menu.show()
if selected_player is None:
    sys.exit(0)
selected_player = players[selected_player]

POLL_RATE = 0.1

def parse_timestamp(stamp):
    try:
        stamp = stamp.split("]")[0][1:].replace(".", ":")
        dt = datetime.strptime(stamp, "%M:%S:%f")
        return dt.minute * 60 + dt.second + dt.microsecond / 1000000
    except:
        return None

def get_position():
    result = playerctl("position")
    return float(result.stdout.strip())


def playerctl(*args):
    return cmd(["playerctl", "-p", selected_player, *args])

def get_playing_song():
    return playerctl("metadata", "--format", "{{title}} -||- {{artist}}").stdout.strip().split(" -||- ")

def wait_until_next_song():
    last_song = get_playing_song()
    while get_playing_song() == last_song:
        last_song = get_playing_song()
        time.sleep(1)
def blockify(text, consoleWidth, font_path="", size=25):
    if settings["font"] == "base":
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoSansCJK-Regular.ttc")
    else:
        font_path = settings["font"]

    font = ImageFont.truetype(font_path, size)
    wrapped = wrap_text(text, font, consoleWidth * (1 if settings["font_style"] == "blocky" else 2))

    measure = ImageDraw.Draw(Image.new("L", (1, 1)))
    l, t, r, b = measure.multiline_textbbox((0, 0), wrapped, font=font)

    lines = []
    if settings["font_style"] == "blocky":
        lines = blocky_lyrics(l, t, r, b, wrapped, font)
    elif settings["font_style"] == "braille":
        lines = braille_lyrics(l, t, r, b, wrapped, font)

    return Text("\n".join(lines))

def blocky_lyrics(l, t, r, b, wrapped, font):
    width = r - l
    height = b - t
    height += height % 2

    img = Image.new("L", (width, height), 0)
    ImageDraw.Draw(img).multiline_text((-l, -t), wrapped, align="center", font=font, fill=255)
    px = img.load()

    lines = []
    for y in range(0, height, 2):
        line = ""
        for x in range(width):
            top_filled = px[x, y] > 0
            bottom_filled = px[x, y+1] > 0

            if top_filled and bottom_filled:
                line += "█"
            elif top_filled:
                line += "▀"
            elif bottom_filled:
                line += "▄"
            else:
                line += " "
        lines.append(line)

    return lines

def braille_lyrics(l, t, r, b, wrapped, font):
    BRAILLE_BITS = {
        (0, 0): 0x01, (0, 1): 0x02, (0, 2): 0x04, (0, 3): 0x40,
        (1, 0): 0x08, (1, 1): 0x10, (1, 2): 0x20, (1, 3): 0x80,
    }
    width = r - l
    width += width % 2
    height = b - t
    height += (4 - height % 4) % 4

    img = Image.new("L", (width, height), 0)
    ImageDraw.Draw(img).multiline_text((-l, -t), wrapped, align="center", font=font, fill=255)
    px = img.load()

    lines = []
    for y in range(0, height, 4):
        line = ""
        for x in range(0, width, 2):
            bits = 0
            for (dx, dy), bit in BRAILLE_BITS.items():
                px_x = x + dx
                py_y = y + dy
                if px_x < width and py_y < height and px[px_x, py_y] > 128:
                    bits |= bit
            line += chr(0x2800 + bits)
        lines.append(line)

    return lines

def wrap_text(text, font, max_width):
    tokens = TOKEN_RE.findall(text)
    lines = []
    current = ""

    for token in tokens:
        candidate = f"{current} {token}".strip()
        if font.getlength(candidate) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = token
    if current:
        lines.append(current)
    return "\n".join(lines)

def main():
    while True:
        console.clear()
        try:
            playing_song, artist = get_playing_song()
            lyrics = syncedlyrics.search(f"{playing_song} {artist}")
        except RequestException as e:
            print(f"Network error {e}")
            wait_until_next_song()
            continue
        except Exception as e:
            print(f"An unexpected error occured {e}")
            wait_until_next_song()
            continue

        if lyrics is None:
            print("no lyrics :(")
            wait_until_next_song()
            continue
        if lyrics == []:
            print("no lyrics :(")
            wait_until_next_song()
            continue

        lyrics = lyrics.split("\n")
        idx = 0
        last_song = get_playing_song()
        global_offset = list(filter(lambda x: "offset" in x.lower(), lyrics))
        if len(global_offset) == 0:
            global_offset = 0
        else:
            global_offset = list(global_offset)[0]
            global_offset = float(global_offset.split(":")[1].strip()[:-1])

        timed_lyrics = []
        for lyric in lyrics:
            timestamp = parse_timestamp(lyric)
            if timestamp is None:
                continue
            timestamp += global_offset

            timed_lyrics.append((timestamp, lyric.split("]")[1].strip()))

        last_song = get_playing_song()

        while True:
            pos = get_position()
            text = list(filter(lambda x: x[0] <= pos+global_offset, timed_lyrics))
            if len(text) == 0:
                continue
            content = text[len(text)-1][1].strip()

            new_song = get_playing_song()
            if new_song != last_song:
                break
            last_song = new_song

            banner = Text(content, justify="center")

            text = Align(
                blockify(content, console.width),
                vertical="middle",
                align="center",
                height=console.height
            )
            console.print(text)

            time.sleep(POLL_RATE)

if __name__ == "__main__":
    main()
