import datetime
import json
import pathlib

import pandas as pd
import yaml

from hydrofia.src import seacarb

NAME_MAPPING = {
'Batch Number': 'batch_nr',
'Bottling Date': 'bottling_date',
'Salinity': 'salinity',
'Total CO2 micromol/kg' : 'dic',
'Total Alkalinity micromol/kg': 'alk'
}

DEFAULT_BATCH_YAML = pathlib.Path('batches.yaml')
DEFAULT_BATCH_JSON = pathlib.Path('batches.json')
NOAA_BATCH_URL = 'https://www.ncei.noaa.gov/access/ocean-carbon-acidification-data-system/oceans/Dickson_CRM/batches.html'


class ReferenceBatch:

    def __init__(self,
                 alk: float | str = None,
                 dic: float | str = None,
                 bottling_date: str | datetime.date | datetime.datetime = None,
                 **kwargs
                 ) -> None:
        self._alk = float(alk)
        self._dic = float(dic)
        self._bottling_date = bottling_date

    @property
    def alk(self) -> float:
        return self._alk

    @property
    def dic(self) -> float:
        return self._dic

    @property
    def bottling_date(self) -> datetime.date:
        if type(self._bottling_date) == datetime.date:
            return self._bottling_date
        if type(self._bottling_date) == datetime.datetime:
            return self._bottling_date.date()
        return datetime.datetime.strptime(self._bottling_date, '%B %d, %Y').date()

    def get_all(self,
                salinity: float = None,
                temperature: float = None) -> dict:
        return seacarb.carb(float(salinity), float(temperature), self.alk, self.dic, 15)

    def get_ph(self,
               salinity: float = None,
               temperature: float = None) -> float:
        return self.get_all(salinity=salinity, temperature=temperature)['pH']


class ReferenceBatches:

    def __init__(self, data: dict):
        self._data = data

    @property
    def latest_batch_nr(self):
        return self.batch_nr_list[-1]

    @property
    def batch_nr_list(self) -> list[str]:
        return sorted(self._data, key=int)

    @property
    def latest_batch(self) -> ReferenceBatch:
        return self.get_batch(self.batch_nr_list[-1])

    def get_batch(self, batch_nr: str | int) -> ReferenceBatch:
        batch_info = self._data.get(str(batch_nr))
        if not batch_info:
            raise Exception(f'Invalid batch number: {batch_nr}')
        return ReferenceBatch(**batch_info)

    def save_as_yaml(self, path: pathlib.Path | str = None) -> None:
        path = path or DEFAULT_BATCH_YAML
        if not path.suffix == 'yaml':
            raise Exception(f'Invalid yaml file to save batches: {path}')
        with open(path, 'w') as fid:
            yaml.safe_dump(self._data, fid)

    def save_as_json(self, path: pathlib.Path | str = None) -> None:
        path = path or DEFAULT_BATCH_JSON
        if not path.suffix == 'json':
            raise Exception(f'Invalid json file to save batches: {path}')
        with open(path, 'w') as fid:
            json.dump(self._data, fid)

    @classmethod
    def from_noaa_url(cls, url: str = None) -> 'ReferenceBatches':
        url = url or NOAA_BATCH_URL
        table = pd.read_html(url)[0]
        table.columns = [NAME_MAPPING.get(col, col) for col in table.columns]
        data = dict()
        for i, row_dict in table.to_dict(orient='index').items():
            data[row_dict['batch_nr'].split()[-1].lstrip('0')] = row_dict
        return cls(data)

    @classmethod
    def from_yaml(cls, path: pathlib.Path | str = None) -> 'ReferenceBatches':
        path = path or DEFAULT_BATCH_YAML
        if not path.exists():
            raise FileNotFoundError(f'No yaml batch file found at: {path}')
        with open(path) as fid:
            return cls(yaml.safe_load(fid))

    @classmethod
    def from_json(cls, path: pathlib.Path | str = None) -> 'ReferenceBatches':
        path = path or DEFAULT_BATCH_JSON
        if not path.exists():
            raise FileNotFoundError(f'No json batch file found at: {path}')
        with open(path) as fid:
            return cls(json.load(fid))


def get_latest_batches():
    try:
        batches = ReferenceBatches.from_noaa_url()
        return batches
    except Exception:
        yaml_batches = None
        json_batches = None
        if DEFAULT_BATCH_YAML.exists():
            yaml_batches = ReferenceBatches.from_yaml()
        if DEFAULT_BATCH_YAML.exists():
            json_batches = ReferenceBatches.from_json()
        if yaml_batches and json_batches:
            if yaml_batches.latest_batch_nr > json_batches.latest_batch_nr:
                return yaml_batches
            return json_batches
        if yaml_batches:
            return yaml_batches
        if json_batches:
            return json_batches
    raise Exception('No batches found!')



