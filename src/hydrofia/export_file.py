from pathlib import Path

import pandas as pd
from pygments.lexers import q

from hydrofia.errors import InvalidHydrofiaFileError

def write_export_file(data: pd.DataFrame, path):
    data.to_csv(path, index=False, sep="\t")


def read_export_file(path: Path, columns: list[str]):
    try:
        data = pd.read_csv(path, header=1)
    except pd.errors.ParserError as e:
        raise InvalidHydrofiaFileError from e

    try:
        selected_columns = data.select(*columns)
    except KeyError as e:
        raise InvalidHydrofiaFileError from e

    return selected_columns
