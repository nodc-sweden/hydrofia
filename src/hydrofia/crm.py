import pandas as pd
import PyCO2SYS

from hydrofia import reference_batch

BATCHES = reference_batch.get_latest_batches()


def calculate_crm(data) -> pd.DataFrame:
    crm_data = data[
        (data["sampleName"].str.contains("CRM|CMR", case=False, na=False))
        & ~(
            data["sampleName"].str.contains("ICOS", case=False, na=False)
        )  # Remove ICOS rows
    ]

    if crm_data.empty:
        return crm_data

    crm_data["batch"] = (
        crm_data["sampleName"]
        .str.replace("CRM|CMR", "", regex=True)
        .str.split("-")
        .str[-1]
    )

    crm_data_with_batch = crm_data.merge(
        BATCHES.data,
        on="batch",
        how="left",
        suffixes=("_sample", ""),
        validate="many_to_one",
    )

    crm_data["reference-pH"] = PyCO2SYS.sys(
        crm_data_with_batch["alk"],
        crm_data_with_batch["dic"],
        1,
        2,
        salinity=crm_data_with_batch["salinity"],
        temperature=crm_data_with_batch["temperatureSample"],
        pressure=0,
        total_silicate=crm_data_with_batch["silicate"],
        total_phosphate=crm_data_with_batch["phosphate"],
        opt_pH_scale=1,
        opt_k_carbonic=10,
        opt_total_borate=1,
    )["pH"]

    crm_data["pH-difference"] = crm_data["pH-tot-labT-P0"] - crm_data["reference-pH"]
    return crm_data
