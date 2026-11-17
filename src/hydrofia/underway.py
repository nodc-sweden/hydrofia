from pathlib import Path

import pandas as pd

from hydrofia import reference_batch
from hydrofia.errors import InvalidHydrofiaFileError
from hydrofia.ph import calculate_ph_t_spec
from hydrofia.tris import calculate_ph_tris_dickson

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

KELVIN_OFFSET = 273.15
BATCHES = reference_batch.get_latest_batches()


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
    underway_data["pH-tot-labT-P0"] = calculate_ph_t_spec(
        underway_data["salinity"],
        underway_data["temperatureSample"],
        underway_data["R0"],
    )
    return underway_data


def calculate_tris(underway_data):
    tris_data = underway_data[
        underway_data["sampleName"].str.contains("TRIS", case=False, na=False)
    ]
    if tris_data.empty:
        return tris_data

    tris_data["reference-pH"] = calculate_ph_tris_dickson(
        35, tris_data["temperatureSample"] + KELVIN_OFFSET
    )
    tris_data["pH-difference"] = tris_data["pH-tot-labT-P0"] - tris_data["reference-pH"]
    return tris_data


def calculate_crm(underway_data):
    crm_data = underway_data[
        underway_data["sampleName"].str.contains("CRM|CMR", case=False, na=False)
    ]
    if crm_data.empty:
        return crm_data
    crm_data["batch"] = crm_data["sampleName"].str.split("-").str[-1]
    unique_batches = {x: BATCHES.get_batch(x) for x in crm_data["batch"].unique()}
    crm_data["reference-pH"] = crm_data.apply(
        lambda x: unique_batches[x["batch"]].get_ph(x["temperatureSample"]), axis=1
    )
    crm_data["pH-difference"] = crm_data["pH-tot-labT-P0"] - crm_data["reference-pH"]
    return crm_data
