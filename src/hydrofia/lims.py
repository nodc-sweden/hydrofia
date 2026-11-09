import pathlib

import pandas as pd


class LimsExport:
    def __init__(self, path):
        self.path = pathlib.Path(path)
        self._data: pd.DataFrame = None

        self._load_file()

    def _load_file(self):
        self._data = pd.read_csv(self.path, sep="\t", encoding="cp1252")
