from rich.live import Live
from rich.text import Text
import time

def render_lyrics(lines, cur_idx):
    text = Text()
    for i, line in enumerate(lines):
        style = "bold cyan" if i == cur_idx else "dim"
        text.append(line + "\n", style=style)
    return text

lines = ["hello", "how are", "you", "today my friend"]
print()

# with Live(render_lyrics(lines, 0), refresh_per_second=4) as live:
#     for i in range(len(lines)):
#         live.update(render_lyrics(lines, i))
#         time.sleep(2)
