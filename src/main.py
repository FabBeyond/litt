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

if subprocess.run(["which", "playerctl"], capture_output=True, text=True).returncode != 0:
    print("Playerctl isnt installed or added to PATH")
    sys.exit(1)

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

def cmd(command):
    return subprocess.run(command, capture_output=True, text=True)

def playerctl(*args):
    return cmd(["playerctl", "-p", selected_player, *args])

def get_playing_song():
    return playerctl("metadata", "--format", "{{title}} -||- {{artist}}").stdout.strip().split(" -||- ")

def wait_until_next_song():
    last_song = get_playing_song()
    while get_playing_song() == last_song:
        last_song = get_playing_song()
        time.sleep(1)
def blockify(text, consoleWidth, font_path="/usr/share/fonts/noto-cjk/NotoSansCJK-Regular.ttc", size=16):
    font = ImageFont.truetype(font_path, size)
    wrapped = wrap_text(text, font, consoleWidth)

    measure = ImageDraw.Draw(Image.new("1", (1, 1)))
    l, t, r, b = measure.multiline_textbbox((0, 0), wrapped, font=font)
    width = r - l
    height = b - t
    height += height % 2

    img = Image.new("1", (width, height), 0)
    ImageDraw.Draw(img).multiline_text((-l, -t), wrapped, align="center", font=font, fill=1)
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

    return Text("\n".join(lines))

def wrap_text(text, font, max_width):
    words = text.split(" ")
    lines = []
    current = ""

    for word in words:
        candidate = f"{current} {word}".strip()
        if font.getlength(candidate) <= max_width or not current:
            current = candidate
        else:
            lines.append(current)
            current = word
    if current:
        lines.append(current)
    return "\n".join(lines)

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
