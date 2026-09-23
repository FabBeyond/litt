from rich.console import Console
from rich.align import Align
from simple_term_menu import TerminalMenu
import time
import requests
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
    dt = datetime.strptime(stamp.split("]")[0][1:], "%M:%S.%f")
    return dt.minute * 60 + dt.second + dt.microsecond / 1000000

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
        response = requests.get("https://lrclib.net/api/search", params={"q": f"{playing_song} {artist}"}, headers={"User-Agent": "terminal-lyrics/0.0.1"})
    except requests.exceptions.RequestException as errex:
        print(f"Exception request: {errex}")
        sys.exit(1)

    if response.status_code != 200:
        print(response.status_code)
        wait_until_next_song()
        continue

    response.encoding = "utf-8"
    data = response.json()
    if len(data) == 0:
        print("no lyrics :(")
        wait_until_next_song()
        continue

    lyrics = data[0]["syncedLyrics"]
    if lyrics is None:
        wait_until_next_song()
        continue

    lyrics = lyrics.split("\n")
    idx = 0
    last_song = get_playing_song()

    while idx < len(lyrics)-1:
        pos = get_position()
        next_time = parse_timestamp(lyrics[idx+1])

        if pos >= next_time:
            idx += 1

            text = Align(
                lyrics[idx].split("]", 1)[1].strip(),
                vertical="middle",
                align="center",
                height=console.height
            )
            console.print(text)
        else:
            time.sleep(min(POLL_RATE, next_time-pos))
