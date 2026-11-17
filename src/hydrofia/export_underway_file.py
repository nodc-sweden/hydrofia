from collections.abc import Sequence
from pathlib import Path

import pandas as pd

UNDERWAY_EXPORT_COLUMNS = (
    "timestamp",
    "sampleName",
    "salinity",
    "temperatureSample",
    "pH-tot-labT-P0",
    "serialIndicator",
    "absorbance434",
    "absorbance487",
    "absorbance578",
    "R0",
    "purified_indicator",
)

UNDERWAY_REFERENCE_EXPORT_COLUMNS = (
    "timestamp",
    "sampleName",
    "salinity",
    "temperatureSample",
    "reference-pH",
    "pH-tot-labT-P0",
    "pH-difference",
    "serialIndicator",
    "absorbance434",
    "absorbance487",
    "absorbance578",
    "R0",
)


def _write_export_file(data: pd.DataFrame, path, columns: Sequence[str]):
    export_data = data[list(columns)]
    export_data.to_csv(path, index=False, sep="\t", encoding="utf-8")


def export_file(data: pd.DataFrame, path: Path):
    _write_export_file(data, path, UNDERWAY_EXPORT_COLUMNS)


def export_reference_file(data: pd.DataFrame, path: Path):
    _write_export_file(data, path, UNDERWAY_REFERENCE_EXPORT_COLUMNS)
