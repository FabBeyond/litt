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

lines = ["hello", "how are", "you", "today my friend"]

response = requests.get("https://lrclib.net/api/search", params={"q": "tetoris"}, headers={"User-Agent": "terminal-lyrics/0.0.1"})
if response.status_code == 200:
    response.encoding = "utf-8"
    data = response.json()
    print(data[0]["syncedLyrics"])

# with Live(render_lyrics(lines, 0), refresh_per_second=4) as live:
#     for i in range(len(lines)):
#         live.update(render_lyrics(lines, i))
#         time.sleep(2)
