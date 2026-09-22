from rich.console import Console
from rich.align import Align
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
    result = subprocess.run(["playerctl", "-p", "spotify", "position"], capture_output=True, text=True)
    return float(result.stdout.strip())

try:
    response = requests.get("https://lrclib.net/api/search", params={"q": "tetoris"}, headers={"User-Agent": "terminal-lyrics/0.0.1"})
    if response.status_code == 200:
        response.encoding = "utf-8"
        data = response.json()
        lyrics = data[0]["syncedLyrics"]
        if lyrics == None:
            pass
        else:
            lyrics = lyrics.split("\n")
            idx = 0
            while idx < len(lyrics)-1:
                pos = get_position()
                next_time = parse_timestamp(lyrics[idx+1])

                if pos >= next_time:
                    idx += 1

                    text = Align(
                        lyrics[idx].split("]")[1][:-1],
                        vertical="middle",
                        align="center",
                        height=console.height
                    )
                    console.print(text)
                else:
                    time.sleep(min(0.2, next_time-pos))
except requests.exceptions.RequestException as errex:
    print("Exception request")

