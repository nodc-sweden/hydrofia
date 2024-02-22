import pathlib
from typing import Tuple, Any

import pandas as pd
import datetime
import numpy as np
from functools import cached_property, cache

EXCLUDE_QUALITY_FLAGS = ['B']


def get_key(**kwargs):
    return f'{kwargs.get("year")}_{kwargs.get("ship")}_{kwargs.get("serno")}'


class CtdStandardFormat:
    DEPTH_PAR = 'DEPH [m]'
    DEPTH_QF_PAR = 'QV:SMHI:DEPH [m]'
    # PRESS_PAR = 'PRES_CTD [dbar]'
    SALT_PAR = 'SALT_CTD [psu]'
    SALT_QF_PAR = 'QV:SMHI:SALT_CTD [psu]'
    TEMP_PAR = 'TEMP_CTD [°C (ITS-90)]'
    TEMP_QF_PAR = 'QV:SMHI:TEMP2_CTD [°C (ITS-90)]'

    def __init__(self, path: pathlib.Path):
        self.path = path

    @cached_property
    def date(self) -> datetime.date:
        return datetime.datetime.strptime(self.path.name.split('_')[2], '%Y%m%d').date()

    @cached_property
    def year(self):
        return self.date.year

    @cached_property
    def ship(self):
        return self.path.name.split('_')[4]

    @cached_property
    def serno(self):
        return self.path.stem.split('_')[-1]

    @cached_property
    def key(self):
        return get_key(year=self.year, ship=self.ship, serno=self.serno)

    @cached_property
    def data(self):
        header = []
        data_lines = []
        with open(self.path, encoding='cp1252') as fid:
            for line in fid:
                if line.startswith('//'):
                    continue
                split_line = line.split('\t')
                if not header:
                    header = split_line
                    continue
                data_lines.append(split_line)
        df = pd.DataFrame(data_lines, columns=header)
        df['depth'] = df[self.DEPTH_PAR].astype(float)
        # df['press'] = df[self.PRESS_PAR].astype(float)
        return df

    @cache
    def get_data_at_depth(self,
                          depth: float,
                          max_depth_diff_allowed: float = None,
                          surface_layer_depth: float = None,
                          bottom_layer_depth: float = None,
                          ) -> pd.DataFrame:
        # print()
        # print('=' * 50)
        # print(f'{self.path=}')
        # print(f'{max_depth_diff_allowed=}')
        # print(f'{surface_layer_depth=}')
        # print(f'{bottom_layer_depth=}')
        # print(f'{depth=}')
        df = self.data.copy(deep=True)
        if surface_layer_depth and depth <= surface_layer_depth:
            df = self.data[self.data['depth'] <= surface_layer_depth].reset_index()
            max_depth_diff_allowed = None
        elif bottom_layer_depth and depth >= bottom_layer_depth:
            df = self.data[self.data['depth'] >= bottom_layer_depth].reset_index()
            max_depth_diff_allowed = None
        if df.empty:
            return pd.DataFrame()
        diff = abs(df['depth'] - depth)
        # print(f'{diff=}')
        min_diff = min(diff)
        # print(f'{min_diff=}')
        # print('-' * 50)
        # print()
        if max_depth_diff_allowed and min_diff > max_depth_diff_allowed:
            return pd.DataFrame()
        return df[diff == min_diff]

    def get_salt_and_temp_data_at_depth(self,
                                        depth: int,
                                        max_depth_diff_allowed: float = None,
                                        surface_layer_depth: float = None,
                                        bottom_layer_depth: float = None) -> (float, float, float):
        df = self.get_data_at_depth(depth,
                                    max_depth_diff_allowed=max_depth_diff_allowed,
                                    surface_layer_depth=surface_layer_depth,
                                    bottom_layer_depth=bottom_layer_depth,
                                    )
        if df.empty:
            return np.nan, np.nan, np.nan
        salt = float(df[self.SALT_PAR].iloc[0])
        if df[self.SALT_QF_PAR].iloc[0] in EXCLUDE_QUALITY_FLAGS:
            salt = np.nan
        temp = float(df[self.TEMP_PAR].iloc[0])
        if df[self.TEMP_QF_PAR].iloc[0] in EXCLUDE_QUALITY_FLAGS:
            temp = np.nan
        depth = float(df[self.DEPTH_PAR].iloc[0])
        if df[self.DEPTH_QF_PAR].iloc[0] in EXCLUDE_QUALITY_FLAGS:
            depth = np.nan
        return salt, temp, depth
        # return float(df[self.SALT_PAR].iloc[0]), float(df[self.TEMP_PAR].iloc[0]), float(df[self.DEPTH_PAR].iloc[0])


class CtdStandardFormatCollection:

    def __init__(self,
                 directory: str | pathlib.Path,
                 max_depth_diff_allowed: float = None,
                 surface_layer_depth: float = None,
                 bottom_layer_depth: float = None,
                 ):

        self.directory = pathlib.Path(directory)
        self._max_depth_diff_allowed = max_depth_diff_allowed
        self._surface_layer_depth = surface_layer_depth
        self._bottom_layer_depth = bottom_layer_depth
        self._files = {}
        self._register_files()

    def _register_files(self):
        self._files = {}
        for path in self.directory.iterdir():
            obj = CtdStandardFormat(path)
            self._files[obj.key] = obj

    def _get_file(self, **kwargs) -> CtdStandardFormat:
        key = get_key(**kwargs)
        return self.files.get(key)

    @property
    def files(self):
        return self._files

    def filter_data_by_date(self, start_date: datetime.date = None, end_date: datetime.date = None):
        files = []
        for file in self.files:
            if start_date and file.date < start_date:
                continue
            if end_date and file.date > end_date:
                continue
            files.append(file)
        self._files = files

    def get_salinity_and_temperature(self,
                                     year: str | int = None,
                                     ship: str | int = None,
                                     serno: str | int = None,
                                     depth: str | int = None) -> tuple[float, float, float]:
        file = self._get_file(year=year, ship=ship, serno=serno)
        if not file:
            return np.nan, np.nan, np.nan
        return file.get_salt_and_temp_data_at_depth(depth,
                                                    max_depth_diff_allowed=self._max_depth_diff_allowed,
                                                    surface_layer_depth=self._surface_layer_depth,
                                                    bottom_layer_depth=self._bottom_layer_depth,
                                                    )


if __name__ == '__main__':
    c = CtdStandardFormat(pathlib.Path(r"C:\svea_ctd\data_local\2023\data\SBE09_1044_20230205_1421_77SE_02_0126.txt"))
    df = c.data


