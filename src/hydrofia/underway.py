from pathlib import Path

import pandas as pd

from hydrofia.errors import InvalidHydrofiaFileError

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
