from typing import Protocol, runtime_checkable
import pandas as pd
import numpy as np
from typing import Type
from .src import seacarb


class HydrofiaTemplateData(Protocol):

    def get_data(self) -> pd.DataFrame:
        ...


class SalinityAndTemperatureData(Protocol):

    def get_ctd_data(self, year: str | int = None, ship: str | int = None, serno: str | int = None,
                              depth: str | int | str = None) -> dict:
        ...


@runtime_checkable
class Exporter(Protocol):

    def save(self, data: pd.DataFrame, **kwargs) -> None:
        ...


class Calculate:
    def __init__(self,
                 hydrofia_data: HydrofiaTemplateData = None,
                 salinity_and_temp_data: SalinityAndTemperatureData = None):
        self.data_hydrofia = hydrofia_data
        self.data_salt_temp = salinity_and_temp_data
        self._data: pd.DataFrame = pd.DataFrame()

    @property
    def data(self):
        return self._data

    def calculate(self):
        self._extract_data()
        self._make_float()
        self._add_salt_and_temp()
        # print('AAA', self._data['salt'])
        self._calculate()
        # print('BBB', self._data['salt'])

    def _extract_data(self):
        # all_data = self.data_hydrofia.get_data()
        self._data = self.data_hydrofia.get_data().copy(deep=True)
        # self._data = all_data[['timestamp', 'year', 'date', 'ship', 'serno', 'depth', 'Rspec']].copy(deep=True)

    def _make_float(self):
        def get_float(val):
            try:
                return float(val)
            except ValueError:
                return val
        self._data['depth'] = self._data['depth'].apply(get_float)
        self._data['Rspec'] = self._data['Rspec'].apply(float)

    def _add_salt_and_temp(self):
        salt_data = []
        temp_data = []
        ref_depth_data = []
        station_data = []
        for index, row in self.data.iterrows():
            if 'CRM' in row['serno'].upper():
                data = dict(
                    salt=float(row['salinity']),
                    temp=float(row['temperatureSample'])
                )
            else:
                depth = row['depth']
                if type(depth) == str:
                    depth = depth.split('/')[0]  # If replicate
                if type(depth) == str and depth.upper() == 'DIB':
                    depth = 'deepest'
                print(f'{row=}')
                data = self.data_salt_temp.get_ctd_data(year=row['year'],
                                                        ship=row['country'] + row['ship'],
                                                        serno=row['serno'],
                                                        depth=depth)
            # raise
            print(f'{data=}')
            salt_data.append(data.get('salt', ''))
            temp_data.append(data.get('temp', ''))
            ref_depth_data.append(data.get('depth', ''))
            station_data.append(data.get('station', ''))
        self._data['salt'] = salt_data
        self._data['temp'] = temp_data
        self._data['ref_depth'] = ref_depth_data
        self._data['station'] = station_data

    def _calculate(self):
        def calc_pHTspec(row):
            if not all([row['salt'], row['temp'], row['Rspec']]):
                return np.nan
            return seacarb.pHTspec(row['salt'], row['temp'], row['Rspec'], 'mosley')
        self._data['calc_pH'] = self._data.apply(calc_pHTspec, axis=1)

    def save_data(self, exporters: list[Exporter] | Exporter, **kwargs) -> None:
        if isinstance(exporters, Exporter):
            exporters = [exporters]
        for exporter in exporters:
            if not isinstance(exporter, Exporter):
                raise NotImplementedError
            exporter.save(self.data, **kwargs)





        # stationsnamn
        # år
        # månad
        # serienummer
        # salthalt
        # temperatur
        # pH

