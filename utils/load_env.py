import json
from pathlib import Path


def load(config_path: str) -> dict:
    path = Path(config_path)
    with open(path) as cf:
        config = json.load(cf)
        return config


if __name__ == '__main__':
    conf = load('../config/config.json')
    print(conf["OPENAI_API_KEY"])
