import datetime
import pathlib

import numpy as np
import pandas as pd
import inspect
import sys
from openpyxl import load_workbook
from openpyxl.styles import PatternFill, Border, Side
from openpyxl.utils import get_column_letter


if getattr(sys, 'frozen', False):
    ROOT_DIR = pathlib.Path(sys.executable).parent
else:
    ROOT_DIR = pathlib.Path(__file__).parent


class ExporterXlsxTemplate:
    name = 'xlsx-template-export'
    template_sheet_name = 'Rapport för utskrift'

    date_cell = [1, 12]
    signature_cell = [2, 12]
    project_cell = [6, 1]
    ctry_code_cell = [6, 6]
    ship_code_cell = [6, 8]
    serno_span_cell = [6, 10]

    data_start_row = 12

    series_col = 3
    depth_col = 6
    ref_depth_col = 7
    salt_col = 8
    temp_col = 9
    ph_calc_col = 10
    ph_col = 11

    def __str__(self):
        return self.__class__.__name__

    def __init__(self, path, overwrite: bool = False):
        self._export_path = pathlib.Path(path)
        self._overwrite = overwrite
        self._template_path = pathlib.Path(ROOT_DIR, 'hydrofia_ph_template.xlsx')
        self._wb = load_workbook(self._template_path)
        self._ws = self._wb[self.template_sheet_name]
        self._data = pd.DataFrame()

    def save(self,
             data: pd.DataFrame,
             signature: str = '',
             project: str = '',
             **kwargs
             ):
        self._data = data
        self._write_header()
        self._write_data()

        self.project = project
        self.signature = signature

        self._save_file()

    def _set_value(self, r: int, c: int, value: str):
        self._ws.cell(r, c).value = value

    def _write_header(self):
        self.date = 'today'
        self._write_ship_code()
        self._write_serno_span()

    def _write_ship_code(self):
        self.ship_code = ', '.join(sorted(set(self.data['ship'])))

    def _write_serno_span(self):
        # TODO: Use sorted set and see if its faster
        int_serno = self.data['serno'].apply(int)
        self.serno_span = f'{str(min(int_serno)).zfill(4)}-{str(max(int_serno)).zfill(4)}'

    def _write_data(self):
        r = self.data_start_row
        for index, df in self.data.groupby(['date', 'serno', 'depth']):
            df = df[~np.isnan(df['calc_pH'])]
            if df.empty:
                continue
            s = df.iloc[-1]
            print(f'{s=}')
            self._set_value(r, self.series_col, s['serno'])
            self._set_value(r, self.depth_col, s['depth'])
            self._set_value(r, self.ref_depth_col, str(float(s['ref_depth'])))
            self._set_value(r, self.salt_col, s['salt'])
            self._set_value(r, self.temp_col, s['temp'])
            self._set_value(r, self.ph_calc_col, s['calc_pH'])
            self._set_value(r, self.ph_col, s['pH'])
            r += 1

    def _save_file(self):
        if self._export_path.exists() and not self._overwrite:
            raise FileExistsError(self._export_path)
        self._wb.save(self._export_path)

    @property
    def data(self):
        return self._data

    @property
    def signature(self):
        return self._ws.cell(*self.signature_cell).value

    @signature.setter
    def signature(self, value):
        self._ws.cell(*self.signature_cell).value = value

    @property
    def date(self):
        return self._ws.cell(*self.date_cell).value

    @date.setter
    def date(self, value):
        if value.lower() == 'today':
            value = str(datetime.datetime.now().date())
        self._ws.cell(*self.date_cell).value = value

    @property
    def project(self):
        return self._ws.cell(*self.project_cell).value

    @project.setter
    def project(self, value):
        self._ws.cell(*self.project_cell).value = value

    @property
    def ctry_code(self):
        return self._ws.cell(*self.ctry_code_cell).value

    @ctry_code.setter
    def ctry_code(self, value):
        self._ws.cell(*self.ctry_code_cell).value = value

    @property
    def ship_code(self):
        return self._ws.cell(*self.ship_code_cell).value

    @ship_code.setter
    def ship_code(self, value):
        self._ws.cell(*self.ship_code_cell).value = value

    @property
    def serno_span(self):
        return self._ws.cell(*self.serno_span_cell).value

    @serno_span.setter
    def serno_span(self, value):
        self._ws.cell(*self.serno_span_cell).value = value


class ExporterTxt:
    name = 'txt-export'

    def __str__(self):
        return self.__class__.__name__

    def __init__(self, path: pathlib.Path | str, overwrite: bool = False):
        self.path = pathlib.Path(path)
        self._overwrite = overwrite

    def save(self, data: pd.DataFrame, **kwargs):
        if self.path.exists() and not self._overwrite:
            raise FileExistsError(self.path)
        leading_cols = ['year', 'ship', 'date', 'serno', 'depth', 'calc_pH', 'salt', 'temp', 'ref_depth', 'Rspec']
        other_cols = [col for col in data.columns if col not in leading_cols]
        new_columns = leading_cols + other_cols
        new_data = data[new_columns]
        if 'index' in new_data.columns:
            new_data.pop('index')
        new_data.to_csv(self.path, sep='\t', index=False)


class Exporters:
    exporters = [
        ExporterTxt,
        ExporterXlsxTemplate
    ]

    @staticmethod
    def get_arguments_from_class(cls):
        return list(inspect.signature(cls).parameters)

    def __init__(self):
        self._exporters = {}
        for cls in Exporters.exporters:
            info = dict(
                cls=cls,
                name=cls.name,
                args=Exporters.get_arguments_from_class(cls)
            )
            self._exporters[info['name']] = info

    def get_exporters(self):
        return self._exporters

    def get_exporter_list(self):
        return list(self._exporters)

    def get_exporter_cls(self, name):
        return self._exporters[name]['cls']

    def get_exporter_args(self, name):
        return self._exporters[name]['args']


if __name__ == '__main__':
    path = pathlib.Path(ROOT_DIR, 'hydrofia_ph_template.xlsx')
    save_path = pathlib.Path(ROOT_DIR, 'hydrofia_ph_template_out.xlsx')
    print(path.exists())
    wb = load_workbook(path)
    ws = wb['Rapport för utskrift']

    e = ExporterXlsxTemplate()
    e.signature = 'MWen'
    e.date = 'today'
    e.ctry_code = 'SE'
    e.ship_code = '77'

    e.save(save_path)

