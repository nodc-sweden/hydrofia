from pathlib import Path

import pandas as pd

from hydrofia.errors import InvalidHydrofiaFileError
from hydrofia.ph import calculate_ph_t_spec

UNDERWAY_COLUMNS = (
    "timestamp",
    "sampleName",
    "action",
    "salinity",
    "temperatureSample",
    "R0",
    "serialIndicator",
    "absorbance434",
    "absorbance487",
    "absorbance578",
)

def read_underway_file(path: Path):
    try:
        data = pd.read_csv(path, header=0, skiprows=[0, 2])
    except pd.errors.ParserError as e:
        raise InvalidHydrofiaFileError from e

    try:
        selected_columns = data.select(*UNDERWAY_COLUMNS)
    except KeyError as e:
        raise InvalidHydrofiaFileError from e

    return selected_columns


def calculate_ph_tot_labt_p0(underway_data):
    underway_data["ph-tot-labT-P0"] = calculate_ph_t_spec(
        underway_data["salinity"],
        underway_data["temperatureSample"],
        underway_data["R0"],
    )
    return underway_data