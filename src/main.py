from rich.console import Console
from rich.align import Align
from simple_term_menu import TerminalMenu
import time
import requests
from datetime import datetime
import subprocess
import sys
import math

if subprocess.run(["which", "playerctl"], capture_output=True, text=True).returncode != 0:
    print("Playerctl isnt installed or added to PATH")
    sys.exit(1)

console = Console()
players = subprocess.run(["playerctl", "-l"], capture_output=True, text=True).stdout.strip()
players = players.split("\n")
selected_player = TerminalMenu(players, title="Choose your playerctl source:")
selected_player = players[selected_player.show()]

def get_time_until_next(line1, line2):
    cur_lyric_time = line1.split("]")[0].replace("[", "")
    next_lyric_time = line2.split("]")[0].replace("[", "")

    date1 = datetime.strptime(cur_lyric_time, "%M:%S.%f")
    date2 = datetime.strptime(next_lyric_time, "%M:%S.%f")

    return (date2-date1).total_seconds()

def parse_timestamp(stamp):
    dt = datetime.strptime(stamp.split("]")[0][1:], "%M:%S.%f")
    return dt.minute * 60 + dt.second + dt.microsecond / 1000000

def get_position():
    result = cmd(["playerctl", "-p", selected_player, "position"])
    return float(result.stdout.strip())

def cmd(command):
    return subprocess.run(command, capture_output=True, text=True)

def get_playing_song():
    return cmd(["playerctl", "-p", selected_player, "metadata", "--format", "'{{title}} -||- {{artist}}'"]).stdout.strip().split(" -||- ")

def wait_until_next_song():
    last_song = get_playing_song()
    while get_playing_song() == last_song:
        last_song = get_playing_song()
        time.sleep(1)

while True:
    try:
        print(123)
        playing_song, artist = get_playing_song()
        response = requests.get("https://lrclib.net/api/search", params={"q": f"{playing_song} {artist}"}, headers={"User-Agent": "terminal-lyrics/0.0.1"})
        if response.status_code == 200:
            response.encoding = "utf-8"
            data = response.json()
            if len(data) == 0:
                print("no lyrics :(")
                wait_until_next_song()
                continue
            lyrics = data[0]["syncedLyrics"]
            if lyrics == "":
                pass
            else:
                lyrics = lyrics.split("\n")
                idx = 0
                last_song = get_playing_song()
                while idx < len(lyrics)-1:
                    pos = get_position()
                    if get_playing_song() != last_song:
                        print("oguqh3ewr4o9gh")
                        break
                    next_time = parse_timestamp(lyrics[idx+1])

                    if pos >= next_time:
                        idx += 1

                        text = Align(
                            lyrics[idx].split("]")[1][1:],
                            vertical="middle",
                            align="center",
                            height=console.height
                        )
                        console.print(text)
                    else:
                        last_song = get_playing_song()
                        time.sleep(min(0.1, next_time-pos))
        else:
            print(response.status_code)
            wait_until_next_song()
    except requests.exceptions.RequestException as errex:
        print("Exception request")

    while cmd(["playerctl", "-p", selected_player, "status"]).stdout.strip() == "Stopped":
        time.sleep(0.5)

