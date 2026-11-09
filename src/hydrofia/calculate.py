from typing import Protocol, runtime_checkable

import numpy as np
import pandas as pd

from hydrofia.ext_src import seacarb


class HydrofiaTemplateData(Protocol):
    def get_data(self) -> pd.DataFrame: ...


class SalinityAndTemperatureData(Protocol):
    def get_ctd_data(
        self,
        year: str | int | None = None,
        ship: str | int | None = None,
        serno: str | int | None = None,
        depth: str | int | None = None,
    ) -> dict: ...


@runtime_checkable
class Exporter(Protocol):
    def save(self, data: pd.DataFrame, **kwargs) -> None: ...


class Calculate:
    def __init__(
        self,
        hydrofia_data: HydrofiaTemplateData = None,
        salinity_and_temp_data: SalinityAndTemperatureData = None,
    ):
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
        self._calculate()

    def _extract_data(self):
        self._data = self.data_hydrofia.get_data().copy(deep=True)

    def _make_float(self):
        def get_float(val):
            try:
                return float(val)
            except ValueError:
                return val

        self._data["depth"] = self._data["depth"].apply(get_float)
        self._data["R0"] = self._data["R0"].apply(get_float)
        self._data["temperatureSample"] = self._data["temperatureSample"].apply(get_float)

    def _add_salt_and_temp(self):
        salt_data = []
        temp_data = []
        ref_depth_data = []
        station_data = []
        for _index, row in self.data.iterrows():
            if "CRM" in row["serno"].upper():
                data = {
                    "salt": float(row["salinity"]),
                    "temp": float(row["temperatureSample"]),
                }
            else:
                depth = row["depth"]
                if type(depth) is str:
                    depth = depth.split("/")[0]  # If replicate
                if type(depth) is str and depth.upper() == "DIB":
                    depth = "deepest"
                data = self.data_salt_temp.get_ctd_data(
                    year=row["year"],
                    ship=row["country"] + row["ship"],
                    serno=row["serno"],
                    depth=depth,
                )
            # raise
            salt_data.append(data.get("salt", ""))
            temp_data.append(data.get("temp", ""))
            ref_depth_data.append(data.get("depth", ""))
            station_data.append(data.get("station", ""))
        self._data["salt"] = salt_data
        self._data["temp"] = temp_data
        self._data["ref_depth"] = ref_depth_data
        self._data["station"] = station_data

    def _calculate(self):
        def calc_ph_t_spec(row):
            if not all([row["salt"], row["temperatureSample"], row["R0"]]):
                return np.nan
            return seacarb.pHTspec(
                row["salt"], row["temperatureSample"] + 273.15, row["R0"], "mueller"
            )

        self._data["pH-tot-labT-P0"] = self._data.apply(calc_ph_t_spec, axis=1)

        def calc_ph_t_spec_at_25(row):
            if not all([row["temperatureSample"], row["pH-tot-labT-P0"]]):
                return np.nan
            return (
                row["pH-tot-labT-P0"] + (25 - row["temperatureSample"]) * -0.01582
            )  # dpH/dT from Millero 2007

        self._data["pH-tot-25C-P0"] = self._data.apply(calc_ph_t_spec_at_25, axis=1)

    def save_data(self, exporters: list[Exporter] | Exporter, **kwargs) -> None:
        if isinstance(exporters, Exporter):
            exporters = [exporters]
        for exporter in exporters:
            if not isinstance(exporter, Exporter):
                raise NotImplementedError
            exporter.save(self.data, **kwargs)
