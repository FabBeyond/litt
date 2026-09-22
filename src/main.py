from rich.live import Live
from rich.text import Text
import time
import requests

def render_lyrics(lines, cur_idx):
    text = Text()
    for i, line in enumerate(lines):
        style = "bold cyan" if i == cur_idx else "dim"
        text.append(line + "\n", style=style)
    return text

try:
    response = requests.get("https://lrclib.net/api/search", params={"q": "Still Shining mayonazy"}, headers={"User-Agent": "terminal-lyrics/0.0.1"})
    if response.status_code == 200:
        response.encoding = "utf-8"
        data = response.json()
        lyrics = data[0]["syncedLyrics"]
        if lyrics == None:
            pass
        else:
            lyrics = lyrics.split("\n")
            with Live(render_lyrics(lyrics, 0), refresh_per_second=4) as live:
                for i in range(len(lyrics)):
                    live.update(render_lyrics(lyrics, i))
                    time.sleep(0.5)

except requests.exceptions.RequestException as errex:
    print("Exception request")

