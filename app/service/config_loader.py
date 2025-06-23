import os
import json

#Replaceble for a DB query later.
BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
DEFAULT_CONFIG_PATH = os.path.join(BASE_DIR, "data", "config", "acme_config.json")

def load_config(config_path: str = DEFAULT_CONFIG_PATH):
    with open(config_path, "r") as f:
        config = json.load(f)
    return config
