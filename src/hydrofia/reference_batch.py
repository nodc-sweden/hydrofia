import json
import pathlib
from dataclasses import dataclass

import pandas as pd
import PyCO2SYS
import yaml

from hydrofia.errors import InvalidBatchError

NAME_MAPPING = {
    "Batch Number": "batch_nr",
    "Salinity": "salinity",
    "Total CO2 micromol/kg": "dic",
    "Total Alkalinity micromol/kg": "alk",
}

DEFAULT_BATCH_YAML = pathlib.Path("batches.yaml")
DEFAULT_BATCH_JSON = pathlib.Path("batches.json")
NOAA_BATCH_URL = "https://www.ncei.noaa.gov/access/ocean-carbon-acidification-data-system/oceans/Dickson_CRM/batches.html"
NOAA_BATCH_FILE = r"\\winfs-proj\data\proj\havgem\MOL\pH\HydroFIA-pH\CRM_Batches.xlsx"


BATCH_FIELDS = ("alk", "dic", "salinity", "phosphate", "silicate")


@dataclass(frozen=True, kw_only=True)
class ReferenceBatch:
    alk: float
    dic: float
    salinity: float
    phosphate: float
    silicate: float

    @classmethod
    def from_dict(cls, data: dict) -> "ReferenceBatch":
        """Create from a row in the NOAA batch table. Other keys are ignored."""
        try:
            return cls(**{name: float(data[name]) for name in BATCH_FIELDS})
        except (KeyError, TypeError, ValueError) as e:
            raise InvalidBatchError(
                f"Missing or invalid value in batch {data.get('batch_nr')}: {e}"
            ) from e

    def get_all(self, temperature: float | None = None) -> dict:
        return PyCO2SYS.sys(
            self.alk,
            self.dic,
            1,
            2,
            salinity=self.salinity,
            temperature=float(temperature),
            pressure=0,
            total_silicate=self.silicate,
            total_phosphate=self.phosphate,
            opt_pH_scale=1,
            opt_k_carbonic=10,
            opt_total_borate=1,
        )
        # return seacarb.carb(
        #   self.salinity, float(temperature), self.alk*1e-06, self.dic*1e-06, 15
        # )

    def get_ph(self, temperature: float | None = None) -> float:
        return self.get_all(temperature=temperature)["pH"]


class ReferenceBatches:
    def __init__(self, data: dict):
        self._data = data
        self.save_as_yaml()

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
            raise InvalidBatchError(f"Unknown batch number: {batch_nr}")
        return ReferenceBatch.from_dict(batch_info)

    def save_as_yaml(self, path: pathlib.Path | str | None = None) -> None:
        path = pathlib.Path(path or DEFAULT_BATCH_YAML)
        if path.suffix != ".yaml":
            raise Exception(f"Invalid yaml file to save batches: {path}")
        with path.open("w") as fid:
            yaml.safe_dump(self._data, fid)

    def save_as_json(self, path: pathlib.Path | str | None = None) -> None:
        path = pathlib.Path(path or DEFAULT_BATCH_JSON)
        if path.suffix != ".json":
            raise Exception(f"Invalid json file to save batches: {path}")
        with path.open("w") as fid:
            json.dump(self._data, fid)

    @classmethod
    def from_noaa_url(cls, url: str | None = None) -> "ReferenceBatches":
        url = url or NOAA_BATCH_URL
        table = pd.read_html(url)[0]
        table.columns = [NAME_MAPPING.get(col, col) for col in table.columns]
        table["batch"] = (
            table["batch_nr"].astype(str).str.extract(r"(\d+)").iloc[:, 0].astype(str)
        )
        nutrients = pd.read_excel(NOAA_BATCH_FILE, dtype=str)
        table = table.merge(
            nutrients[["batch", "phosphate", "silicate"]], on="batch", how="left"
        )
        table = table.drop(columns=["batch"])
        data = {}
        for row_dict in table.to_dict(orient="index").values():
            data[row_dict["batch_nr"].split()[-1].lstrip("0")] = row_dict
        return cls(data)

    @classmethod
    def from_yaml(cls, path: pathlib.Path | str | None = None) -> "ReferenceBatches":
        path = pathlib.Path(path or DEFAULT_BATCH_YAML)
        if not path.exists():
            raise FileNotFoundError(f"No yaml batch file found at: {path}")
        with path.open() as fid:
            return cls(yaml.safe_load(fid))

    @classmethod
    def from_json(cls, path: pathlib.Path | str | None = None) -> "ReferenceBatches":
        path = pathlib.Path(path or DEFAULT_BATCH_JSON)
        if not path.exists():
            raise FileNotFoundError(f"No json batch file found at: {path}")
        with path.open() as fid:
            return cls(json.load(fid))


def get_latest_batches():
    try:
        return ReferenceBatches.from_noaa_url()
    except Exception:
        yaml_batches = None
        json_batches = None
        if DEFAULT_BATCH_YAML.exists():
            yaml_batches = ReferenceBatches.from_yaml()
        if DEFAULT_BATCH_JSON.exists():
            json_batches = ReferenceBatches.from_json()
        if yaml_batches and json_batches:
            if yaml_batches.latest_batch_nr > json_batches.latest_batch_nr:
                return yaml_batches
            return json_batches
        if yaml_batches:
            return yaml_batches
        if json_batches:
            return json_batches
    raise Exception("No batches found!")
