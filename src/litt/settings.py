from simple_term_menu import TerminalMenu
from litt.utils import initialize_config, get_config_value, set_config_value, save_config

initialize_config()

font_options = ["Style", "Font", "Font Size"]
font_menu = TerminalMenu(font_options, title="Settings")
answer = font_menu.show()

if answer == 0:
    style_options = ["Blocky", "Braille"]
    style_menu = TerminalMenu(style_options, title="Font Style")
    answer = style_menu.show()

    if answer == 0:
        set_config_value("font_style", "blocky")
    elif answer == 1:
        set_config_value("font_style", "braille")

elif answer == 1:
    fontfont_options = ["Base", "Custom"]
    fontfont_menu = TerminalMenu(fontfont_options, title="Font")
    answer = fontfont_menu.show()

    if answer == 0:
        set_config_value("font", "base")
    elif answer == 1:
        set_config_value("font", input("Custom Font Path: "))

elif answer == 2:
    set_config_value("font_size", float(input(f"Set custom font size (cur: {get_config_value('font_size')}): ")))

save_config()
