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
import termios
import tty
import select

from litt.utils import initialize_config, get_config_value, set_config_value, save_config, is_cached, get_cached, add_cache

def cmd(command):
    return subprocess.run(command, capture_output=True, text=True)

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
def blockify(text, consoleWidth, font_path=""):
    size = get_config_value("font_size")
    if get_config_value("font") == "base":
        font_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "fonts", "NotoSansCJK-Regular.ttc")
    else:
        font_path = get_config_value("font")

    font = ImageFont.truetype(font_path, size)
    wrapped = wrap_text(text, font, consoleWidth * (1 if get_config_value("font_style") == "blocky" else 2))

    measure = ImageDraw.Draw(Image.new("L", (1, 1)))
    l, t, r, b = measure.multiline_textbbox((0, 0), wrapped, font=font)

    lines = []
    if get_config_value("font_style") == "blocky":
        lines = blocky_lyrics(l, t, r, b, wrapped, font)
    elif get_config_value("font_style") == "braille":
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


old_settings = termios.tcgetattr(sys.stdin.fileno())

initialize_config()

parser = argparse.ArgumentParser("LITT")
parser.add_argument("--settings", action="store_true")
args = parser.parse_args()
if args.settings:
    from litt import settings
    sys.exit(1)


if cmd(["which", "playerctl"]).returncode != 0:
    print("Playerctl isnt installed or added to PATH")
    sys.exit(1)
if cmd(["playerctl", "-l"]).stdout.strip() == "":
    print("No playerctl source")
    sys.exit(1)

console = Console()
players = subprocess.run(["playerctl", "-l"], capture_output=True, text=True).stdout.strip()
players = players.split("\n")
player_menu = TerminalMenu(players, title="Choose your playerctl source:")
selected_player = player_menu.show()
if selected_player is None:
    sys.exit(0)
selected_player = players[selected_player]

TOKEN_RE = re.compile(
    r'[\u3040-\u30ff\u3400-\u4dbf\u4e00-\u9fff\uf900-\ufaff\uff66-\uff9f\uac00-\ud7a3]'
    r'|\s+'
    r'|\S+'
)
POLL_RATE = 0.1

tty.setcbreak(sys.stdin.fileno())

def get_lyrics(force_fetch=False):
    playing_song, artist = get_playing_song()
    search_term = f"{playing_song} {artist}"

    lyrics = ""
    if is_cached(search_term) and not force_fetch:
        lyrics = get_cached(search_term)
    else:
        lyrics = fetch_lyrics(search_term)
        if lyrics == False:
            print("no lyrics :(")
            return False, 0
        add_cache(search_term, lyrics)

    if lyrics == False:
        print("no lyrics :(")
        return False, 0

    lyrics = lyrics.split("\n")

    global_offset = get_global_offset(search_term)
    timed_lyrics = []
    for lyric in lyrics:
        timestamp = parse_timestamp(lyric)
        if timestamp is None:
            continue
        timestamp += global_offset

        timed_lyrics.append((timestamp, lyric.split("]")[1].strip()))



    return timed_lyrics, global_offset
def fetch_lyrics(search_term):
    try:
        lyrics = syncedlyrics.search(search_term)
        if lyrics is None or lyrics == "":
            return False

        return lyrics
    except RequestException as e:
        print(f"Network error {e}")
        return False
    except Exception as e:
        print(f"An unexpected error occured {e}")
        return False
def get_global_offset(lyrics):
    global_offset = list(filter(lambda x: "offset" in x.lower(), lyrics))
    if len(global_offset) == 0:
        global_offset = 0
    else:
        global_offset = list(global_offset)[0]
        global_offset = float(global_offset.split(":")[1].strip()[:-1])

    return global_offset

def main():
    try:
        force_fetch = False
        while True:
            console.clear()
            timed_lyrics, global_offset = get_lyrics(force_fetch=force_fetch)
            force_fetch = False
            if timed_lyrics == False:
                wait_until_next_song()
                continue

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

                ready, _, _ = select.select([sys.stdin], [], [], POLL_RATE)
                if ready:
                    key = sys.stdin.read(1)
                    if key == "q":
                        sys.exit(0)
                    elif key == ",":
                        set_config_value("font_size", get_config_value("font_size") - 1)
                    elif key == ".":
                        set_config_value("font_size", get_config_value("font_size") + 1)
                    elif key == "r":
                        break
                    elif key == "R":
                        force_fetch = True
                        break
                    elif key == "j":
                        # adjust song offset
                        pass
                    elif key == "k":
                        # adjust song offset
                        pass
                    elif key == "J":
                        # adjust global offset
                        pass
                    elif key == "K":
                        # adjust global offset
                        pass
    finally:
        save_config()
        termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_settings)

if __name__ == "__main__":
    main()
