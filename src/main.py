from rich.console import Console
from rich.align import Align
import time
import requests
from datetime import datetime

console = Console()

def get_time_until_next(line1, line2):
    cur_lyric_time = line1.split("]")[0].replace("[", "")
    next_lyric_time = line2.split("]")[0].replace("[", "")

    date1 = datetime.strptime(cur_lyric_time, "%M:%S.%f")
    date2 = datetime.strptime(next_lyric_time, "%M:%S.%f")

    return (date2-date1).total_seconds()

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
            for idx, line in enumerate(lyrics):
                text = line.split("]")[1]

                text = Align(
                    text,
                    vertical="middle",
                    align="center",
                    height=console.height
                )
                console.print(text)
                time.sleep(get_time_until_next(line, lyrics[idx+1]))

except requests.exceptions.RequestException as errex:
    print("Exception request")

