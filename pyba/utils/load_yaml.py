from pathlib import Path

import yaml

current_file = Path(__file__)


def load_config():
    config_path = current_file.parent.parent / "config.yaml"
    with open(config_path, "r") as f:
        return yaml.safe_load(f)
