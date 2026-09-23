from rich.console import Console
from rich.align import Align
from simple_term_menu import TerminalMenu
import syncedlyrics
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
        dt = datetime.strptime(stamp.split("]")[0][1:], "%M:%S.%f")
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

while True:
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

        text = Align(
            content,
            vertical="middle",
            align="center",
            height=console.height
        )
        console.print(text)

        time.sleep(POLL_RATE)
