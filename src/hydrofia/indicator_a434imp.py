import pathlib

import pandas as pd
import yaml

from datetime import datetime


NAME_MAPPING = {
    'Datum': 'measurement_date',
    'serialIndicator': 'serial_indicator',
    'A434imp': 'a434imp',
    'Kommentar': 'comment'
}

DEFAULT_INDICATOR_A434_IMP_TXT = pathlib.Path('indicator_a434imp.txt')
INDICATOR_FILE = r'\\winfs-proj\data\proj\havgem\MOL\pH\HydroFIA-pH\Indikator_A434imp.xlsx'


class IndicatorBatch:

    def __init__(self,
                 a434imp: float | str = None,
                 **kwargs
                 ) -> None:
        self._a434imp = float(a434imp)

    @property
    def a434imp(self) -> float:
        return self._a434imp


class IndicatorBatches:

    def __init__(self, indicator_data: dict):
        self._indicator_data = indicator_data

    def get_a434imp(self, serial_indicator: str) -> float:
        batch_info = self._indicator_data.get(str(serial_indicator))
        if not batch_info:
            print(f'No measurements of A434 impurities for serial number: {serial_indicator}')
            a434imp_value = float('nan')
        else:
            a434imp_value = float(IndicatorBatch(**batch_info).a434imp)
        return a434imp_value

    @classmethod
    def from_server(cls, file_path: str = None) -> 'IndicatorBatches':
        file_path = file_path or INDICATOR_FILE
        table = pd.read_excel(file_path, header=6)
        table.columns = [NAME_MAPPING.get(col, col) for col in table.columns]
        table.to_csv('indicator_a434imp.txt', sep='\t', index=False)
        data = dict()
        for i, row_dict in table.to_dict(orient='index').items():
            data[row_dict['serial_indicator']] = row_dict
        return cls(data)

    @classmethod
    def from_txt(cls, file_path: str = None) -> 'IndicatorBatches':
        file_path = file_path or DEFAULT_INDICATOR_A434_IMP_TXT
        table = pd.read_csv(file_path)
        data = dict()
        for i, row_dict in table.to_dict(orient='index').items():
            data[row_dict['serial_indicator']] = row_dict
        return cls(data)


def get_latest_indicator_batches():
    try:
        indicator_values = IndicatorBatches.from_server()
        return indicator_values
    except Exception:
        txt_batches = None
        if DEFAULT_INDICATOR_A434_IMP_TXT.exists():
            txt_batches = pd.read_csv(DEFAULT_INDICATOR_A434_IMP_TXT)
        if txt_batches:
            return txt_batches
    raise Exception('No batches found!')



