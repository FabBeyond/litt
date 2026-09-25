from simple_term_menu import TerminalMenu
import os
import json

config_dir = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
config_file = os.path.join(config_dir, "litt", "config.json")
settings = json.loads(open(config_file, "r").read())

font_options = ["Style", "Font", "Font Size"]
font_menu = TerminalMenu(font_options, title="Settings")
answer = font_menu.show()

if answer == 0:
    style_options = ["Blocky", "Braille"]
    style_menu = TerminalMenu(style_options, title="Font Style")
    answer = style_menu.show()

    if answer == 0:
        settings["font_style"] = "blocky"
    elif answer == 1:
        settings["font_style"] = "braille"

elif answer == 1:
    fontfont_options = ["Base", "Custom"]
    fontfont_menu = TerminalMenu(fontfont_options, title="Font")
    answer = fontfont_menu.show()

    if answer == 0:
        settings["font"] = "base"
    elif answer == 1:
        settings["font"] = input("Custom Font Path: ")

elif answer == 2:
    settings["font_size"] = float(input(f"Set custom font size (cur: {settings['font_size']}): "))

open(config_file, "w").write(json.dumps(settings, indent=2))
