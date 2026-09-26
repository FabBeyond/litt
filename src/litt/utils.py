import json
import os
import sys

config_dir = os.environ.get("XDG_CONFIG_HOME", os.path.expanduser("~/.config"))
config_path = os.path.join(config_dir, "litt")
config_file = os.path.join(config_path, "config.json")

DEFAULTS = {"font": "base", "font_style": "blocky", "font_size": 25}
config = {}

def initialize_config():
    global config
    os.makedirs(config_path, exist_ok=True)
    if not os.path.isfile(config_file):
        with open(config_file, "w") as f:
            f.write(json.dumps(DEFAULTS, indent=2))

    try:
        with open(config_file, "r") as f:
            config = json.loads(f.read())
    except json.JSONDecodeError:
        print("Invalid config! Make sure the config file is a valid json.")
        sys.exit(1)

    if not set(DEFAULTS.keys()).issubset(config):
        config = {**DEFAULTS, **config}

def get_config_value(val):
    return config[val]
def set_config_value(key, val):
    config[key] = val
def save_config():
    with open(config_file, "w") as f:
        f.write(json.dumps(config, indent=2))
