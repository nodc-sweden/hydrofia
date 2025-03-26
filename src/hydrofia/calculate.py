from typing import Protocol, runtime_checkable
import pandas as pd
import numpy as np
from typing import Type
from hydrofia.indicator_a434imp import IndicatorBatches, IndicatorBatch
from hydrofia.ext_src import seacarb


class HydrofiaTemplateData(Protocol):

    def get_data(self) -> pd.DataFrame:
        ...


class SalinityAndTemperatureData(Protocol):

    def get_ctd_data(self, year: str | int = None, ship: str | int = None, serno: str | int = None,
                              depth: str | int | str = None) -> dict:
        ...


class A434Impurities(IndicatorBatches):

    def a434imp_value(self, serial_indicator: str = None) -> float:
        ...


@runtime_checkable
class Exporter(Protocol):

    def save(self, data: pd.DataFrame, **kwargs) -> None:
        ...


class Calculate:
    def __init__(self,
                 hydrofia_data: HydrofiaTemplateData = None,
                 salinity_and_temp_data: SalinityAndTemperatureData = None,
                 a434imp_data: A434Impurities = None
                 ):
        self.data_hydrofia = hydrofia_data
        self.data_salt_temp = salinity_and_temp_data
        self.data_a434imp = a434imp_data
        self._data: pd.DataFrame = pd.DataFrame()

    @property
    def data(self):
        return self._data

    def calculate(self):
        self._extract_data()
        self._make_float()
        self._add_salt_and_temp()
        self._add_a434imp()
        # print('AAA', self._data['salt'])
        self._calculate()
        # print('BBB', self._data['salt'])

    def _extract_data(self):
        # all_data = self.data_hydrofia.get_data()
        self._data = self.data_hydrofia.get_data().copy(deep=True)

    def _make_float(self):
        def get_float(val):
            try:
                return float(val)
            except ValueError:
                return val
        self._data['depth'] = self._data['depth'].apply(get_float)
        self._data['R0'] = self._data['R0'].apply(get_float)
        self._data['temperatureSample'] = self._data['temperatureSample'].apply(get_float)

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
                data = self.data_salt_temp.get_ctd_data(year=row['year'],
                                                        ship=row['country'] + row['ship'],
                                                        serno=row['serno'],
                                                        depth=depth)
            # raise
            salt_data.append(data.get('salt', ''))
            temp_data.append(data.get('temp', ''))
            ref_depth_data.append(data.get('depth', ''))
            station_data.append(data.get('station', ''))
        self._data['salt'] = salt_data
        self._data['temp'] = temp_data
        self._data['ref_depth'] = ref_depth_data
        self._data['station'] = station_data

    def _add_a434imp(self):
        a434imp = []
        for index, row in self.data.iterrows():
            a434imp.append(self.data_a434imp.get_a434imp(row['serialIndicator']))
        self._data['a434imp'] = a434imp

    def _calculate(self):
        def calc_Rpure(row):
            if not all([row['R0'], row['absorbance434'], row['a434imp']]):
                return np.nan
            return float(row['R0']) * (1 + (row['a434imp'] / (float(row['absorbance434']) - row['a434imp'])))

        self._data['Rpure'] = self._data.apply(calc_Rpure, axis=1)
        def calc_pHTspec(row):
            # if not all([row['salt'], row['temperatureSample'], row['Rpure']]):
            if not all([row['salt'], row['temperatureSample'], row['R0']]):
                return np.nan
            # return seacarb.pHTspec(row['salt'], row['temperatureSample'], row['Rpure'], 'mosley')
            return seacarb.pHTspec(row['salt'], row['temperatureSample'], row['R0'], 'mosley')
        # self._data['calc_pH'] = self._data.apply(calc_pHTspec, axis=1).apply(lambda x: str(x).replace(',', '.'))
        self._data['calc_pH'] = self._data.apply(calc_pHTspec, axis=1)

        def calc_pHTspec_at_25(row):
            if not all([row['temperatureSample'], row['calc_pH']]):
                return np.nan
            return row['calc_pH']+(25-row['temperatureSample'])*-0.01582  # dpH/dT from Millero 2007
        self._data['calc_pH_at_25'] = self._data.apply(calc_pHTspec_at_25, axis=1)

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

