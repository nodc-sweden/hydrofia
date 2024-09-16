import pathlib
import pandas as pd


class LimsExport:

    def __init__(self, path):
        self.path = pathlib.Path(path)
        self._data: pd.DataFrame = None

        self._load_file()

    def _load_file(self):
        self._data = pd.read_csv(self.path, sep='\t', encoding='cp1252')


if __name__ == '__main__':
    path = r"C:\mw\utv\HydroFIA\data\2023-03-03 1606-2023-LANDSKOD 77-FARTYGSKOD 10\Raw_data\data.txt"
    le = LimsExport(path)