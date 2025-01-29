from pathlib import Path

import yaml


class Config(dict):
    def __init__(self, path: Path):
        print(f"Reading config from: {path.absolute()}")
        data = yaml.load(path.read_text(), Loader=yaml.CLoader)
        self.update(data)
        self._path = path

    def save(self):
        with self._path.open("w+") as fd:
            yaml.dump(dict(self), fd)
