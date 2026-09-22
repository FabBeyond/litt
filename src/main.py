from rich.console import Console
from rich.align import Align
import time
import requests

console = Console()

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
            for line in lyrics:
                text = Align(
                    line,
                    vertical="middle",
                    align="center",
                    height=console.height
                )
                console.print(text)

except requests.exceptions.RequestException as errex:
    print("Exception request")

