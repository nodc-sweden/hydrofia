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

def write_export_file(data: pd.DataFrame, path):
    export_data = data[list(UNDERWAY_EXPORT_COLUMNS)]
    export_data.to_csv(path, index=False, sep="\t", encoding="utf-8")
